"""
Consolidador de Inadimplências — Versão Web
Multi-empresa: Ineprotec / Matrícula EaD (Fase D)
"""

import json
import os
import pickle
import secrets
import shutil
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


def _checar_dependencias():
    """Mensagem amigável se faltar lib de terceiros, em vez de stack trace cru (STORY-01-07).

    Roda antes de importar pandas/flask/etc., de modo que um ambiente sem as deps
    receba uma instrução clara em vez de um ImportError no meio do arquivo.
    """
    import importlib.util
    faltando = [p for p in ('flask', 'flask_login', 'pandas', 'openpyxl')
                if importlib.util.find_spec(p) is None]
    if faltando:
        print("=" * 60)
        print("  ERRO: dependências faltando: " + ", ".join(faltando))
        print("  Instale com:  pip install -r requirements.txt")
        print("=" * 60)
        raise SystemExit(1)


_checar_dependencias()

import pandas as pd
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import (
    LoginManager, UserMixin, current_user,
    login_user, logout_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

import database as db
import processing as proc
from processing import fmt_brl

# ---------------------------------------------------------------------------
# Caminhos — estrutura de dados em C:\MATINE\
# ---------------------------------------------------------------------------

DATA_DIR    = Path(r'C:\MATINE')
UPLOADS_DIR = DATA_DIR / 'uploads'    # uploads/{EMPRESA}/{tipo}/  ← detecção por pasta
RELATORIOS  = DATA_DIR / 'relatorios' # relatorios/{EMPRESA}/{ano}/{mes}/{dia}/
LOGS_DIR    = DATA_DIR / 'logs'
ESTADO_DIR  = DATA_DIR / 'estado'
BANCO_DIR   = DATA_DIR / 'banco'
CRM_PASTA   = DATA_DIR / 'crm-exports'
ENV_PATH    = Path(__file__).resolve().parent / '.env'


# ---------------------------------------------------------------------------
# Leitura/escrita simples do .env (sem dependência externa)
# ---------------------------------------------------------------------------

def _env_get(chave: str) -> str | None:
    """Lê uma chave do .env. Retorna None se ausente ou vazia."""
    if ENV_PATH.exists():
        for linha in ENV_PATH.read_text(encoding='utf-8').splitlines():
            if linha.startswith(chave + '='):
                valor = linha.split('=', 1)[1].strip()
                return valor or None
    return None


def _env_set(chave: str, valor: str):
    """Acrescenta chave=valor ao .env (gitignored). Usado para semear na 1ª execução."""
    with ENV_PATH.open('a', encoding='utf-8') as f:
        f.write(f'{chave}={valor}\n')


def _carregar_secret_key() -> str:
    """FLASK_SECRET_KEY do .env; gera e persiste na primeira execução.

    Mantém a secret_key fora do código-fonte e estável entre reinícios
    (sessões Flask não são invalidadas a cada restart).
    """
    chave = _env_get('FLASK_SECRET_KEY')
    if chave:
        return chave
    nova_chave = secrets.token_hex(32)
    _env_set('FLASK_SECRET_KEY', nova_chave)
    return nova_chave


def _carregar_credenciais() -> tuple[str, str]:
    """Usuário único + hash da senha (STORY-01-06). Semeia defaults na 1ª execução.

    APP_USUARIO e APP_SENHA ficam no .env (gitignored). A senha é guardada como
    hash pbkdf2 — nunca em texto plano. Default de fábrica: luana / matine2026,
    trocável regenerando o hash (ver .env.example).
    """
    usuario = _env_get('APP_USUARIO')
    if not usuario:
        usuario = 'luana'
        _env_set('APP_USUARIO', usuario)
    senha_hash = _env_get('APP_SENHA')
    if not senha_hash:
        senha_hash = generate_password_hash('matine2026', method='pbkdf2:sha256')
        _env_set('APP_SENHA', senha_hash)
    return usuario, senha_hash

# ---------------------------------------------------------------------------
# Flask
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = _carregar_secret_key()
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

APP_USUARIO, APP_SENHA_HASH = _carregar_credenciais()

# ---------------------------------------------------------------------------
# Autenticação (Flask-Login — usuário único MVP, STORY-01-06)
# ---------------------------------------------------------------------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar o sistema.'
login_manager.login_message_category = 'warning'

# Endpoints liberados sem login. Tudo o mais é negado por padrão (default-deny)
# via before_request — assim novas rotas (ex.: webhooks da Fase H) já nascem
# protegidas sem depender de lembrar de decorar cada uma.
_ENDPOINTS_PUBLICOS = {'login', 'logout', 'static'}


class _Usuario(UserMixin):
    """Usuário único do sistema. O id é o nome de usuário configurado."""
    def __init__(self, user_id: str):
        self.id = user_id


@login_manager.user_loader
def _load_user(user_id: str):
    return _Usuario(user_id) if user_id == APP_USUARIO else None


@app.before_request
def _exigir_login():
    if request.endpoint in _ENDPOINTS_PUBLICOS:
        return
    if not current_user.is_authenticated:
        return redirect(url_for('login', next=request.path))


@app.template_filter('brl')
def brl_filter(val):
    return fmt_brl(float(val))


def _log(msg: str):
    ts = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linha = f"[{ts}] {msg}"
    print(linha)
    try:
        with open(LOGS_DIR / "app_web.log", 'a', encoding='utf-8') as f:
            f.write(linha + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Multi-empresa
# ---------------------------------------------------------------------------

EMPRESA_LABELS = {
    'INEPROTEC':   'Ineprotec',
    'MATRICULAEAD': 'Mat. EaD',
}


def get_empresa() -> str:
    return session.get('empresa', 'INEPROTEC')


@app.context_processor
def inject_empresa():
    emp = get_empresa()
    return {
        'empresa_ativa':  emp,
        'empresa_label':  EMPRESA_LABELS.get(emp, emp),
        'empresa_labels': EMPRESA_LABELS,
        'sessao_ativa':   _estado_file(emp).exists(),
    }


@app.route('/empresa/<nome>')
def trocar_empresa(nome):
    if nome in db.EMPRESAS:
        session['empresa'] = nome
        _log(f"Empresa alterada para: {nome}")
    return redirect(request.referrer or url_for('index'))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MESES = {
    1: '01-Janeiro', 2: '02-Fevereiro', 3: '03-Marco',
    4: '04-Abril',   5: '05-Maio',      6: '06-Junho',
    7: '07-Julho',   8: '08-Agosto',    9: '09-Setembro',
    10: '10-Outubro', 11: '11-Novembro', 12: '12-Dezembro',
}

EXTS_VALIDAS = {'.csv', '.xlsx', '.xls'}


def _pasta_relatorio(empresa: str) -> Path:
    """Pasta datada para os relatórios gerados."""
    hoje  = datetime.now()
    pasta = RELATORIOS / empresa / str(hoje.year) / MESES[hoje.month] / f"{hoje.day:02d}"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _detectar_arquivo(tipo: str, empresa: str) -> Path | None:
    """Retorna o arquivo mais recente na pasta de upload do tipo/empresa.
    Detecção por localização — o nome do arquivo não importa."""
    pasta = UPLOADS_DIR / empresa / tipo
    if not pasta.exists():
        return None
    arquivos = [f for f in pasta.iterdir()
                if f.is_file() and f.suffix.lower() in EXTS_VALIDAS]
    return max(arquivos, key=lambda f: f.stat().st_mtime) if arquivos else None


def _estado_file(empresa: str) -> Path:
    return ESTADO_DIR / f"estado_{empresa.lower()}.pkl"


def _salvar_estado(consolidado: pd.DataFrame, stats: dict, empresa: str,
                   avencer: pd.DataFrame | None = None,
                   stats_avencer: dict | None = None):
    with open(_estado_file(empresa), 'wb') as f:
        pickle.dump({
            'consolidado':   consolidado,
            'stats':         stats,
            'avencer':       avencer,
            'stats_avencer': stats_avencer,
        }, f)


def _carregar_estado(empresa: str) -> tuple[
    pd.DataFrame | None, dict | None,
    pd.DataFrame | None, dict | None
]:
    arq = _estado_file(empresa)
    if not arq.exists():
        return None, None, None, None
    try:
        with open(arq, 'rb') as f:
            estado = pickle.load(f)
        consolidado   = estado['consolidado']
        stats         = estado['stats']
        avencer       = estado.get('avencer')
        stats_avencer = estado.get('stats_avencer')

        # Migra categorias antigas (A/B/Régua)
        cats_antigas = {'A', 'B', 'Régua'}
        if 'Categoria' in consolidado.columns and consolidado['Categoria'].isin(cats_antigas).any():
            def _reclassificar(row):
                d = row['Dias_Atraso']
                if d == 1: return 'Novos Inadimplentes'
                if d <= 29: return 'Inadimplentes Mês'
                return 'Acima 30 Dias'
            consolidado['Categoria'] = consolidado.apply(_reclassificar, axis=1)
            stats['cat_novos']   = int((consolidado['Categoria'] == 'Novos Inadimplentes').sum())
            stats['cat_mes']     = int((consolidado['Categoria'] == 'Inadimplentes Mês').sum())
            stats['cat_acima30'] = int((consolidado['Categoria'] == 'Acima 30 Dias').sum())
            _salvar_estado(consolidado, stats, empresa, avencer, stats_avencer)

        return consolidado, stats, avencer, stats_avencer
    except Exception:
        return None, None, None, None


def _limpar_estado(empresa: str):
    arq = _estado_file(empresa)
    if arq.exists():
        arq.unlink()


# ---------------------------------------------------------------------------
# Inicialização — setup idempotente da estrutura C:\MATINE\ (STORY-01-07)
# ---------------------------------------------------------------------------

def setup_inicial() -> bool:
    """Prepara o ambiente para rodar. Idempotente — seguro chamar a cada boot.

    Passos:
      1. Detecta primeira execução (ausência do banco).
      2. Cria a estrutura de pastas em C:\\MATINE (uploads por empresa/tipo,
         relatórios, estado, logs, banco, crm-exports).
      3. db.init_db() — schema versionado (migrations) + templates padrão por empresa.
      4. Loga a conclusão; sinaliza se foi a primeira execução.

    Retorna True se esta foi a primeira execução (banco ainda não existia).
    """
    primeira_vez = not db.DB_PATH.exists()

    for _emp in db.EMPRESAS:
        for _tipo in ('vencidos', 'avencer', 'alunos', 'pagos_cancelados'):
            (UPLOADS_DIR / _emp / _tipo).mkdir(parents=True, exist_ok=True)
        (RELATORIOS / _emp).mkdir(parents=True, exist_ok=True)
    for _dir in (ESTADO_DIR, LOGS_DIR, BANCO_DIR, CRM_PASTA):
        _dir.mkdir(parents=True, exist_ok=True)

    db.init_db()

    if primeira_vez:
        _log(f"Primeira execução: estrutura criada em {DATA_DIR} e banco inicializado.")
    else:
        _log("Setup verificado (estrutura e banco já existentes).")
    return primeira_vez


PRIMEIRA_EXECUCAO = setup_inicial()


# ---------------------------------------------------------------------------
# Rotas — Autenticação (STORY-01-06)
# ---------------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        senha   = request.form.get('senha', '')
        if usuario == APP_USUARIO and check_password_hash(APP_SENHA_HASH, senha):
            login_user(_Usuario(usuario), remember=True)
            _log(f"Login bem-sucedido: {usuario}")
            destino = request.args.get('next', '')
            # Evita open redirect: só aceita caminhos internos (começam com '/' e não '//').
            if not destino.startswith('/') or destino.startswith('//'):
                destino = url_for('index')
            return redirect(destino)
        flash("Usuário ou senha incorretos.", "danger")
        _log(f"Login falhou para usuário: {usuario!r}")
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    empresa = get_empresa()
    consolidado, stats, _, _ = _carregar_estado(empresa)
    auto = {
        'alunos':            _detectar_arquivo('alunos',            empresa),
        'vencidos':          _detectar_arquivo('vencidos',           empresa),
        'avencer':           _detectar_arquivo('avencer',            empresa),
        'pagos_cancelados':  _detectar_arquivo('pagos_cancelados',   empresa),
    }
    base_info = db.status_base(empresa)
    return render_template(
        'index.html',
        auto=auto,
        stats=stats,
        tem_consolidacao=(consolidado is not None),
        base_info=base_info,
    )


@app.route('/upload', methods=['POST'])
def upload():
    empresa = get_empresa()
    tipo    = request.form.get('tipo')
    if tipo not in ('alunos', 'vencidos', 'avencer', 'pagos_cancelados'):
        flash("Tipo de arquivo inválido.", "danger")
        return redirect(url_for('index'))

    arquivo = request.files.get('arquivo')
    if not arquivo or arquivo.filename == '':
        flash("Nenhum arquivo selecionado.", "warning")
        return redirect(url_for('index'))

    pasta_destino = UPLOADS_DIR / empresa / tipo
    pasta_destino.mkdir(parents=True, exist_ok=True)
    destino = pasta_destino / arquivo.filename
    arquivo.save(str(destino))

    _log(f"[{empresa}] Arquivo importado ({tipo}): {destino}")
    flash(f"✅ Arquivo '{arquivo.filename}' importado com sucesso!", "success")
    return redirect(url_for('index'))


@app.route('/consolidar', methods=['POST'])
def consolidar():
    empresa = get_empresa()
    _limpar_estado(empresa)

    path_vencidos = _detectar_arquivo('vencidos', empresa)
    path_alunos   = _detectar_arquivo('alunos',   empresa)

    if not path_vencidos:
        flash("Arquivo de Vencidos não encontrado. Importe-o primeiro.", "danger")
        return redirect(url_for('index'))
    if not path_alunos:
        flash("Arquivo de Clientes não encontrado. Importe-o primeiro.", "danger")
        return redirect(url_for('index'))

    try:
        consolidado, stats = proc.consolidar(path_vencidos, path_alunos)

        # Tentar processar AVENCER se disponível (Fase E)
        avencer, stats_avencer = None, None
        path_avencer = _detectar_arquivo('avencer', empresa)
        if path_avencer:
            try:
                avencer, stats_avencer = proc.consolidar_avencer(path_avencer, path_alunos)
                if avencer.empty:
                    avencer, stats_avencer = None, None
            except Exception as e_av:
                _log(f"[{empresa}] AVENCER ignorado: {e_av}")

        _salvar_estado(consolidado, stats, empresa, avencer, stats_avencer)
        _log(f"[{empresa}] Consolidação: {stats['total']} clientes | "
             f"Novos={stats['cat_novos']} Mês={stats['cat_mes']} Acima30={stats['cat_acima30']}"
             + (f" | AVencer={stats_avencer['total']}" if stats_avencer else ""))

        msg = (f"✅ [{EMPRESA_LABELS[empresa]}] Consolidação concluída! {stats['total']} clientes — "
               f"Novos: {stats['cat_novos']} | Mês (2-29d): {stats['cat_mes']} | "
               f"Acima 30 Dias: {stats['cat_acima30']} | Total: {fmt_brl(stats['valor_total'])}")
        if stats_avencer and stats_avencer.get('total', 0) > 0:
            msg += f" | 🔔 A Vencer amanhã: {stats_avencer['total']}"
        flash(msg, "success")

        if stats.get('sem_cadastro', 0) > 0:
            nomes_sc = ', '.join(stats['sem_cadastro_nomes'][:5])
            mais     = f" e mais {stats['sem_cadastro'] - 5}" if stats['sem_cadastro'] > 5 else ''
            flash(
                f"⚠️ {stats['sem_cadastro']} cliente(s) sem cadastro no arquivo de Clientes: {nomes_sc}{mais}",
                "warning"
            )
        return redirect(url_for('resultado'))
    except Exception as e:
        _log(f"[{empresa}] ERRO consolidar: {e}")
        flash(f"Erro ao consolidar: {e}", "danger")
        return redirect(url_for('index'))


@app.route('/resultado')
def resultado():
    empresa = get_empresa()
    consolidado, stats, avencer, stats_avencer = _carregar_estado(empresa)
    if consolidado is None:
        flash("Nenhuma consolidação em curso. Consolide primeiro.", "warning")
        return redirect(url_for('index'))

    linhas = []
    for _, row in consolidado.iterrows():
        linhas.append({
            'nome':       row['Aluno'],
            'cpf':        row['CPF'],
            'telefone':   row['Telefone'] if pd.notna(row.get('Telefone', None)) else '-',
            'email':      row['E-mail']   if pd.notna(row.get('E-mail',   None)) else '-',
            'qtd':        int(row['Qtd_Boletos']),
            'valor':      fmt_brl(row['Total']),
            'valor_raw':  float(row['Total']),
            'vencimento': row['Ultimo_Vencimento'].strftime('%d/%m/%Y'),
            'dias':       int(row['Dias_Atraso']),
            'categoria':  row['Categoria'],
        })

    avencer_linhas = []
    if avencer is not None and not avencer.empty:
        for _, row in avencer.iterrows():
            avencer_linhas.append({
                'nome':       row['Aluno'],
                'cpf':        row['CPF'],
                'telefone':   row['Telefone'] if pd.notna(row.get('Telefone', None)) else '-',
                'qtd':        int(row['Qtd_Boletos']),
                'valor':      fmt_brl(row['Total']),
                'valor_raw':  float(row['Total']),
                'vencimento': row['Proximo_Vencimento'].strftime('%d/%m/%Y'),
                'categoria':  row.get('Categoria', 'A Vencer'),
            })

    return render_template('resultado.html', linhas=linhas, stats=stats,
                           avencer_linhas=avencer_linhas, stats_avencer=stats_avencer)


@app.route('/gerar-relatorio', methods=['POST'])
def gerar_relatorio():
    empresa = get_empresa()
    consolidado, stats, avencer, _ = _carregar_estado(empresa)
    if consolidado is None:
        flash("Consolide primeiro.", "warning")
        return redirect(url_for('index'))

    templates_list = db.get_templates_completo(empresa)
    pasta    = _pasta_relatorio(empresa)
    data_str = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    gerados       = []
    cpfs_cobrados = []
    total_msgs    = 0

    try:
        # Agrupar cada aluno no template correspondente ao seu dias_atraso
        grupos: dict[int, dict] = {}   # template_id → {template, rows[]}
        sem_template = []

        for _, row in consolidado.iterrows():
            tmpl = _encontrar_template(int(row['Dias_Atraso']), templates_list)
            if tmpl:
                tid = tmpl['id']
                if tid not in grupos:
                    grupos[tid] = {'template': tmpl, 'rows': []}
                grupos[tid]['rows'].append(row)
            else:
                sem_template.append(row['Aluno'])

        # Gerar um arquivo por template
        for tid, grupo in grupos.items():
            tmpl    = grupo['template']
            dados_g = pd.DataFrame(grupo['rows'])
            proc.gerar_txt_template(tmpl['titulo'], tmpl['conteudo'], dados_g, data_str, pasta)
            proc.gerar_xlsx_template(tmpl['titulo'], dados_g, data_str, pasta)
            gerados.append(f"{tmpl['titulo']}: {len(dados_g)} clientes")
            cpfs_cobrados.extend(dados_g['CPF'].astype(str).str.zfill(11).tolist())
            total_msgs += len(dados_g)

        if sem_template:
            _log(f"[{empresa}] {len(sem_template)} cliente(s) sem template correspondente: "
                 f"{', '.join(sem_template[:5])}")
            flash(
                f"⚠️ {len(sem_template)} cliente(s) sem template para seus dias de atraso "
                f"(verifique Configurações → Mensagens): {', '.join(sem_template[:3])}",
                "warning"
            )

        # A Vencer — template com dias_de < 0 ou categoria 'A Vencer'
        tmpl_avencer = next(
            (t for t in templates_list
             if t['categoria'] == 'A Vencer'
             or (t['dias_de'] is not None and t['dias_de'] < 0)),
            None
        )
        if avencer is not None and not avencer.empty and tmpl_avencer:
            proc.gerar_txt_avencer(avencer, data_str, pasta, tmpl_avencer['conteudo'])
            proc.gerar_xlsx_avencer(avencer, data_str, pasta)
            gerados.append(f"A Vencer: {len(avencer)} clientes")
            total_msgs += len(avencer)

        if cpfs_cobrados:
            db.incrementar_cobrancas(cpfs_cobrados, empresa)

        _log(f"[{empresa}] Relatórios gerados: {', '.join(gerados)}")
        flash(
            f"✅ Relatórios gerados com sucesso para {empresa}. "
            f"{total_msgs} mensagens prontas para envio "
            f"({', '.join(gerados)}) → {pasta}",
            "success"
        )
    except Exception as e:
        _log(f"[{empresa}] ERRO gerar-relatorio: {e}")
        flash(f"Erro ao gerar relatórios: {e}", "danger")

    return redirect(url_for('resultado'))


@app.route('/atualizar-base', methods=['POST'])
def atualizar_base():
    empresa = get_empresa()
    consolidado, _, avencer_atual, _ = _carregar_estado(empresa)
    if consolidado is None:
        flash("Consolide primeiro.", "warning")
        return redirect(url_for('index'))

    # Usa TODOS os CPFs do A Vencer (não só janela 0-3 dias) para detectar renegociação.
    # Caso: admin apaga fatura vencida e cria nova com data futura → aluno some dos vencidos
    # mas ainda aparece no A Vencer além dos 3 dias → deve ser RENEGOCIADO, não QUITADO.
    cpfs_avencer = set()
    path_avencer = _detectar_arquivo('avencer', empresa)
    if path_avencer:
        try:
            cpfs_avencer = proc.obter_cpfs_avencer(path_avencer)
            _log(f"[{empresa}] A Vencer (todos): {len(cpfs_avencer)} CPFs para cruzamento de renegociação")
        except Exception as e_av:
            _log(f"[{empresa}] A Vencer CPFs ignorado: {e_av}")
            # Fallback: usa o que foi processado na sessão (só 0-3 dias)
            if avencer_atual is not None and not avencer_atual.empty and 'CPF' in avencer_atual.columns:
                mask = avencer_atual['CPF'].astype(str).str.strip() != ''
                cpfs_avencer = set(avencer_atual.loc[mask, 'CPF'].astype(str).str.zfill(11))

    cpfs_pagos, cpfs_cancelados = None, None
    path_pc = _detectar_arquivo('pagos_cancelados', empresa)
    if path_pc:
        try:
            cpfs_pagos, cpfs_cancelados = proc.processar_pagos_cancelados(path_pc)
            _log(f"[{empresa}] pagos_cancelados: {len(cpfs_pagos)} pagos, {len(cpfs_cancelados)} cancelados")
        except Exception as e_pc:
            _log(f"[{empresa}] pagos_cancelados ignorado: {e_pc}")
            flash(f"⚠️ Relatório de Pagos/Cancelados não processado: {e_pc}", "warning")

    try:
        base_antes = db.carregar_base(empresa)
        diff       = db.salvar_base(consolidado, empresa, cpfs_avencer=cpfs_avencer,
                                    cpfs_pagos=cpfs_pagos, cpfs_cancelados=cpfs_cancelados)

        pasta    = _pasta_relatorio(empresa)
        data_str = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

        novos_df  = consolidado[consolidado['CPF'].astype(str).str.zfill(11).isin(diff['novos'])]
        saidos_df = base_antes[base_antes['cpf'].isin(diff['saidos'])]

        gerados = []
        if len(novos_df) > 0:
            proc.gerar_relatorio_novos(novos_df, data_str, pasta)
            gerados.append(f"{len(novos_df)} novos inadimplentes")

        if len(saidos_df) > 0:
            saidos_df = saidos_df.rename(columns={
                'cpf': 'CPF', 'aluno': 'Aluno', 'telefone': 'Telefone',
                'email': 'E-mail', 'data_entrada': 'Data_Entrada', 'categoria': 'Categoria'
            })
            proc.gerar_relatorio_saidos(saidos_df, data_str, pasta)
            gerados.append(f"{len(saidos_df)} saíram dos vencidos")

        _log(f"[{empresa}] Base atualizada: total={diff['total']} "
             f"novos={len(diff['novos'])} saidos={len(diff['saidos'])} "
             f"renegociados={len(diff['saidos_renegociados'])} quitados={len(diff['saidos_quitados'])} "
             f"cancelados={len(diff['saidos_cancelados'])}")
        flash(
            f"✅ Base atualizada! Total: {diff['total']} registros. "
            f"Novos: {len(diff['novos'])} | Em Renegociação: {len(diff['saidos_renegociados'])} | "
            f"Pagos: {len(diff['saidos_quitados'])} | Cancelados: {len(diff['saidos_cancelados'])} | "
            f"Continuam: {diff['continuam']}",
            "success"
        )
        if gerados:
            flash(f"📁 Relatórios: {', '.join(gerados)} salvos em {pasta}", "info")

    except Exception as e:
        _log(f"[{empresa}] ERRO atualizar-base: {e}")
        flash(f"Erro ao atualizar base: {e}", "danger")

    return redirect(url_for('base'))


@app.route('/base')
def base():
    empresa = get_empresa()
    df      = db.carregar_base(empresa)
    info    = db.status_base(empresa)

    _, _, avencer, stats_avencer = _carregar_estado(empresa)
    cpfs_avencer     = set()
    cpfs_vence_hoje  = set()
    vence_hoje_count = 0
    if avencer is not None and not avencer.empty and 'CPF' in avencer.columns:
        mask = avencer['CPF'].astype(str).str.strip() != ''
        cpfs_avencer = set(avencer.loc[mask, 'CPF'].astype(str).str.zfill(11))
        if 'Categoria' in avencer.columns:
            mask_hoje = (avencer['Categoria'] == 'Vence Hoje') & mask
            cpfs_vence_hoje  = set(avencer.loc[mask_hoje, 'CPF'].astype(str).str.zfill(11))
            vence_hoje_count = int(mask_hoje.sum())

    alunos = []
    for _, row in df.iterrows():
        cpf = str(row['cpf']).zfill(11)
        alunos.append({
            'cpf':             cpf,
            'aluno':           row['aluno'],
            'telefone':        row['telefone'] or '-',
            'email':           row['email'] or '-',
            'qtd':             row['qtd_boletos'],
            'total':           fmt_brl(float(row['total'])),
            'vencimento':      row['ultimo_vencimento'],
            'dias':            row['dias_atraso'],
            'categoria':       row['categoria'],
            'status':          row['status'],
            'entrada':         row['data_entrada'],
            'qtd_cobranca':    row['qtd_cobranca'] if row['qtd_cobranca'] else 0,
            'em_renegociacao': cpf in cpfs_avencer,
            'vence_hoje':      cpf in cpfs_vence_hoje,
        })
    return render_template('base.html', alunos=alunos, info=info,
                           vence_hoje_count=vence_hoje_count)


@app.route('/base/limpar', methods=['POST'])
def limpar_base():
    empresa = get_empresa()
    db.limpar_base(empresa)
    _limpar_estado(empresa)
    _log(f"[{empresa}] Base limpa pelo usuário.")
    flash("🗑️ Base de inadimplentes limpa com sucesso.", "success")
    return redirect(url_for('base'))


@app.route('/base/status', methods=['POST'])
def atualizar_status():
    empresa = get_empresa()
    cpf     = request.form.get('cpf')
    status  = request.form.get('status')
    if cpf and status in ('INADIMPLENTE', 'QUITADO', 'RENEGOCIADO', 'CANCELADO'):
        db.atualizar_status_aluno(cpf, status, empresa)
        flash(f"Status de {cpf} atualizado para {status}.", "success")
    return redirect(url_for('base'))


@app.route('/configuracoes')
def configuracoes():
    empresa      = get_empresa()
    templates    = db.get_templates_completo(empresa)
    auto_alunos  = _detectar_arquivo('alunos', empresa)
    config_email = db.get_config_email(empresa) or {}
    # A senha SMTP nunca vai para o HTML (STORY-01-04). Passamos só um flag para a UI
    # decidir entre mostrar bullets ("já configurada") ou pedir a senha.
    smtp_senha_set = bool(config_email.get('smtp_senha'))
    config_email = {**config_email, 'smtp_senha': ''}
    return render_template('configuracoes.html',
                           templates=templates,
                           auto_alunos=auto_alunos,
                           config_email=config_email,
                           smtp_senha_set=smtp_senha_set)


def _encontrar_template(dias_atraso: int, templates: list) -> dict | None:
    """Retorna o template mais específico (maior dias_de) cujo intervalo cobre dias_atraso."""
    candidatos = [
        t for t in templates
        if t['dias_de'] is not None
        and t['dias_de'] >= 0          # exclui templates A Vencer (dias_de < 0)
        and t['dias_de'] <= dias_atraso
        and (t['dias_ate'] is None or t['dias_ate'] >= dias_atraso)
    ]
    return max(candidatos, key=lambda t: t['dias_de']) if candidatos else None


def _parse_dia(val: str) -> int | None:
    try:
        return int(val.strip())
    except (ValueError, AttributeError):
        return None


@app.route('/configuracoes/template/novo', methods=['POST'])
def template_novo():
    empresa  = get_empresa()
    titulo   = request.form.get('titulo',   '').strip()
    conteudo = request.form.get('conteudo', '').strip()
    dias_de  = _parse_dia(request.form.get('dias_de',  ''))
    dias_ate = _parse_dia(request.form.get('dias_ate', ''))
    tag_crm  = request.form.get('tag_crm', '').strip()
    if titulo and conteudo:
        db.criar_template(titulo, conteudo, empresa, dias_de, dias_ate, tag_crm)
        flash(f"✅ Mensagem '{titulo}' criada com sucesso!", "success")
    else:
        flash("Título e mensagem são obrigatórios.", "warning")
    return redirect(url_for('configuracoes'))


@app.route('/configuracoes/template/<int:tid>/editar', methods=['POST'])
def template_editar(tid: int):
    empresa  = get_empresa()
    titulo   = request.form.get('titulo',   '').strip()
    conteudo = request.form.get('conteudo', '').strip()
    dias_de  = _parse_dia(request.form.get('dias_de',  ''))
    dias_ate = _parse_dia(request.form.get('dias_ate', ''))
    tag_crm  = request.form.get('tag_crm', '').strip()
    if titulo and conteudo:
        db.salvar_template(tid, titulo, conteudo, empresa, dias_de, dias_ate, tag_crm)
        flash(f"✅ Mensagem '{titulo}' atualizada com sucesso!", "success")
    else:
        flash("Título e mensagem são obrigatórios.", "warning")
    return redirect(url_for('configuracoes'))


@app.route('/configuracoes/template/<int:tid>/excluir', methods=['POST'])
def template_excluir(tid: int):
    empresa = get_empresa()
    db.excluir_template(tid, empresa)
    flash("🗑️ Mensagem excluída.", "info")
    return redirect(url_for('configuracoes'))


@app.route('/abrir-relatorios')
def abrir_relatorios():
    empresa = get_empresa()
    pasta   = _pasta_relatorio(empresa)
    os.startfile(str(pasta))
    flash(f"Pasta de relatórios aberta: {pasta}", "info")
    return redirect(url_for('resultado') if _carregar_estado(empresa)[0] is not None else url_for('index'))


@app.route('/limpar')
def limpar():
    empresa = get_empresa()
    _limpar_estado(empresa)
    flash("Dados da consolidação limpos.", "info")
    return redirect(url_for('index'))


@app.route('/ajuda')
def ajuda():
    """Central de Ajuda — explica, em linguagem operacional, como usar cada tela."""
    return render_template('ajuda.html')


# ---------------------------------------------------------------------------
# Fase F — Wizard de Envio WhatsApp
# ---------------------------------------------------------------------------

def _formatar_mensagem_wizard(row, tmpl: dict, col_venc: str = 'Ultimo_Vencimento') -> str:
    nome = row['Aluno']
    primeiro_nome = nome.split()[0].capitalize()
    tratamento = proc.detectar_tratamento(nome)
    venc_raw = row.get(col_venc)
    venc = venc_raw.strftime('%d/%m/%Y') if hasattr(venc_raw, 'strftime') else str(venc_raw)
    return tmpl['conteudo'].format_map(proc._SafeFormat(
        TRATAMENTO=tratamento, NOME=primeiro_nome, DATA_VENCIMENTO=venc,
    ))


@app.route('/envio-mensagens')
def envio_mensagens():
    empresa = get_empresa()
    consolidado, stats, avencer, stats_avencer = _carregar_estado(empresa)
    if consolidado is None:
        flash("Consolide primeiro.", "warning")
        return redirect(url_for('index'))

    templates_list = db.get_templates_completo(empresa)
    enviados_hoje  = {e['cpf'] for e in db.get_envios_hoje(empresa, 'whatsapp')}
    emails_hoje    = {e['cpf'] for e in db.get_envios_hoje(empresa, 'email')}
    tem_email_cfg  = bool(db.get_config_email(empresa) and
                          db.get_config_email(empresa).get('smtp_host'))

    linhas = []
    for _, row in consolidado.iterrows():
        tmpl = _encontrar_template(int(row['Dias_Atraso']), templates_list)
        if tmpl is None:
            continue
        cpf    = str(row['CPF']).zfill(11)
        email  = row.get('E-mail') if pd.notna(row.get('E-mail', None)) else ''
        linhas.append({
            'cpf':       cpf,
            'nome':      row['Aluno'],
            'telefone':  row['Telefone'] if pd.notna(row.get('Telefone', None)) else '-',
            'email':     email or '-',
            'tem_email': bool(email),
            'dias':      int(row['Dias_Atraso']),
            'valor':     fmt_brl(row['Total']),
            'categoria': row['Categoria'],
            'template':  tmpl['titulo'],
            'mensagem':  _formatar_mensagem_wizard(row, tmpl),
            'enviado':   cpf in enviados_hoje,
            'email_enviado': cpf in emails_hoje,
        })

    avencer_linhas = []
    if avencer is not None and not avencer.empty:
        tmpl_av = next(
            (t for t in templates_list
             if t['categoria'] == 'A Vencer'
             or (t['dias_de'] is not None and t['dias_de'] < 0)),
            None
        )
        if tmpl_av:
            for _, row in avencer.iterrows():
                cpf   = str(row.get('CPF', '')).zfill(11) if row.get('CPF', '') else ''
                email = row.get('E-mail') if pd.notna(row.get('E-mail', None)) else ''
                avencer_linhas.append({
                    'cpf':       cpf,
                    'nome':      row['Aluno'],
                    'telefone':  row['Telefone'] if pd.notna(row.get('Telefone', None)) else '-',
                    'email':     email or '-',
                    'tem_email': bool(email),
                    'valor':     fmt_brl(row['Total']),
                    'vencimento': row['Proximo_Vencimento'].strftime('%d/%m/%Y'),
                    'categoria': row.get('Categoria', 'A Vencer'),
                    'template':  tmpl_av['titulo'],
                    'mensagem':  _formatar_mensagem_wizard(row, tmpl_av, 'Proximo_Vencimento'),
                    'enviado':   cpf in enviados_hoje,
                    'email_enviado': cpf in emails_hoje,
                })

    total_todos    = len(linhas) + len(avencer_linhas)
    total_enviados = sum(1 for l in linhas if l['enviado']) + \
                     sum(1 for l in avencer_linhas if l['enviado'])
    pct = int(total_enviados / total_todos * 100) if total_todos > 0 else 0

    return render_template(
        'envio_mensagens.html',
        linhas=linhas,
        avencer_linhas=avencer_linhas,
        stats=stats,
        total_todos=total_todos,
        total_enviados=total_enviados,
        pct=pct,
        tem_email_cfg=tem_email_cfg,
    )


@app.route('/whatsapp/marcar-enviado', methods=['POST'])
def whatsapp_marcar_enviado():
    empresa  = get_empresa()
    cpf      = request.form.get('cpf', '').strip()
    template = request.form.get('template', '')
    if cpf:
        db.registrar_envio(cpf, empresa, 'whatsapp', template)
    return ('', 204)


@app.route('/whatsapp/marcar-todos', methods=['POST'])
def whatsapp_marcar_todos():
    empresa = get_empresa()
    consolidado, _, avencer, _ = _carregar_estado(empresa)
    if consolidado is not None:
        templates_list = db.get_templates_completo(empresa)
        for _, row in consolidado.iterrows():
            tmpl = _encontrar_template(int(row['Dias_Atraso']), templates_list)
            if tmpl:
                db.registrar_envio(str(row['CPF']).zfill(11), empresa, 'whatsapp', tmpl['titulo'])
        if avencer is not None and not avencer.empty:
            tmpl_av = next(
                (t for t in templates_list
                 if t['categoria'] == 'A Vencer'
                 or (t['dias_de'] is not None and t['dias_de'] < 0)),
                None
            )
            if tmpl_av:
                for _, row in avencer.iterrows():
                    cpf = str(row.get('CPF', '')).zfill(11) if row.get('CPF', '') else ''
                    if cpf:
                        db.registrar_envio(cpf, empresa, 'whatsapp', tmpl_av['titulo'])
    flash("✅ Todos os clientes marcados como enviados no WhatsApp.", "success")
    return redirect(url_for('envio_mensagens'))


# ---------------------------------------------------------------------------
# Fase G — Cobranças por E-mail
# ---------------------------------------------------------------------------

def _enviar_email_smtp(config: dict, dest: str, assunto: str, mensagem: str):
    """Envia um e-mail via SMTP. Lança exceção em caso de erro."""
    from_name = config.get('smtp_from_name') or 'Cobranças'
    remetente = f"{from_name} <{config['smtp_usuario']}>"

    msg = MIMEMultipart('alternative')
    msg['From']    = remetente
    msg['To']      = dest
    msg['Subject'] = assunto

    html_body = (
        "<html><body style='font-family:Arial,sans-serif;max-width:600px;"
        "margin:auto;padding:20px;color:#333'>"
        + mensagem.replace('\n', '<br>')
        + "</body></html>"
    )
    msg.attach(MIMEText(mensagem, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    if config.get('smtp_tls', 1):
        server = smtplib.SMTP(config['smtp_host'], int(config['smtp_port']), timeout=15)
        server.starttls()
    else:
        server = smtplib.SMTP_SSL(config['smtp_host'], int(config['smtp_port']), timeout=15)
    server.login(config['smtp_usuario'], config['smtp_senha'])
    server.sendmail(config['smtp_usuario'], [dest], msg.as_string())
    server.quit()


def _assunto_padrao(categoria: str, empresa_label: str) -> str:
    mapa = {
        'A Vencer':            f'Seu boleto vence amanhã — {empresa_label}',
        'Novos Inadimplentes': f'Boleto em aberto — {empresa_label}',
        'Inadimplentes Mês':   f'Boleto em aberto — {empresa_label}',
        'Acima 30 Dias':       f'Parcelas em aberto — {empresa_label}',
    }
    return mapa.get(categoria, f'Notificação financeira — {empresa_label}')


@app.route('/email/configurar', methods=['POST'])
def email_configurar():
    empresa   = get_empresa()
    host      = request.form.get('smtp_host', '').strip()
    port      = int(request.form.get('smtp_port', 587) or 587)
    usuario   = request.form.get('smtp_usuario', '').strip()
    senha     = request.form.get('smtp_senha', '').strip()
    from_name = request.form.get('smtp_from_name', '').strip()
    tls       = request.form.get('smtp_tls') == '1'
    db.salvar_config_email(empresa, host, port, usuario, senha, from_name, tls)
    flash("✅ Configurações de e-mail salvas com sucesso.", "success")
    return redirect(url_for('configuracoes') + '#tab-email')


@app.route('/email/testar', methods=['POST'])
def email_testar():
    empresa = get_empresa()
    config  = db.get_config_email(empresa)
    if not config or not config.get('smtp_host'):
        flash("Configure o servidor SMTP primeiro.", "warning")
        return redirect(url_for('configuracoes') + '#tab-email')
    try:
        if config.get('smtp_tls', 1):
            srv = smtplib.SMTP(config['smtp_host'], int(config['smtp_port']), timeout=10)
            srv.starttls()
        else:
            srv = smtplib.SMTP_SSL(config['smtp_host'], int(config['smtp_port']), timeout=10)
        srv.login(config['smtp_usuario'], config['smtp_senha'])
        srv.quit()
        flash("✅ Conexão SMTP testada com sucesso!", "success")
    except Exception as e:
        flash(f"❌ Erro na conexão SMTP: {e}", "danger")
    return redirect(url_for('configuracoes') + '#tab-email')


@app.route('/email/assunto/<int:tid>', methods=['POST'])
def email_assunto(tid: int):
    empresa = get_empresa()
    assunto = request.form.get('assunto_email', '').strip()
    db.salvar_assunto_template(tid, assunto, empresa)
    flash("✅ Assunto de e-mail salvo.", "success")
    return redirect(url_for('configuracoes') + '#tab-email')


@app.route('/email/enviar-aluno', methods=['POST'])
def email_enviar_aluno():
    empresa = get_empresa()
    cpf     = request.form.get('cpf', '').strip()
    config  = db.get_config_email(empresa)

    if not config or not config.get('smtp_host'):
        return jsonify(ok=False, erro='SMTP não configurado. Configure em Configurações → E-mail.'), 400

    consolidado, _, avencer, _ = _carregar_estado(empresa)
    if consolidado is None:
        return jsonify(ok=False, erro='Sem consolidação'), 400

    templates_list = db.get_templates_completo(empresa)
    emp_label = EMPRESA_LABELS.get(empresa, empresa)

    # Procura no consolidado
    row_found = None
    for _, row in consolidado.iterrows():
        if str(row['CPF']).zfill(11) == cpf:
            row_found = row
            break

    # Procura no avencer se não achou
    is_avencer = False
    if row_found is None and avencer is not None and not avencer.empty:
        for _, row in avencer.iterrows():
            if str(row.get('CPF', '')).zfill(11) == cpf:
                row_found = row
                is_avencer = True
                break

    if row_found is None:
        return jsonify(ok=False, erro='Aluno não encontrado'), 404

    email_dest = row_found.get('E-mail') if pd.notna(row_found.get('E-mail', None)) else None
    if not email_dest:
        return jsonify(ok=False, erro='Aluno sem e-mail cadastrado'), 400

    if is_avencer:
        tmpl = next(
            (t for t in templates_list
             if t['categoria'] == 'A Vencer'
             or (t['dias_de'] is not None and t['dias_de'] < 0)),
            None
        )
        col_venc = 'Proximo_Vencimento'
        categoria = 'A Vencer'
    else:
        tmpl = _encontrar_template(int(row_found['Dias_Atraso']), templates_list)
        col_venc = 'Ultimo_Vencimento'
        categoria = row_found['Categoria']

    if not tmpl:
        return jsonify(ok=False, erro='Sem template para este aluno'), 400

    mensagem = _formatar_mensagem_wizard(row_found, tmpl, col_venc)
    assunto  = tmpl.get('assunto_email') or _assunto_padrao(categoria, emp_label)

    try:
        _enviar_email_smtp(config, email_dest, assunto, mensagem)
        db.registrar_envio(cpf, empresa, 'email', tmpl['titulo'])
        _log(f"[{empresa}] E-mail enviado para {row_found['Aluno']} <{email_dest}>")
        return jsonify(ok=True)
    except Exception as e:
        _log(f"[{empresa}] ERRO e-mail para {cpf}: {e}")
        return jsonify(ok=False, erro=str(e)), 500


@app.route('/email/enviar-todos', methods=['POST'])
def email_enviar_todos():
    empresa = get_empresa()
    config  = db.get_config_email(empresa)

    if not config or not config.get('smtp_host'):
        flash("Configure o servidor SMTP em Configurações → E-mail.", "warning")
        return redirect(url_for('envio_mensagens'))

    consolidado, _, avencer, _ = _carregar_estado(empresa)
    if consolidado is None:
        flash("Consolide primeiro.", "warning")
        return redirect(url_for('index'))

    templates_list = db.get_templates_completo(empresa)
    emails_hoje    = {e['cpf'] for e in db.get_envios_hoje(empresa, 'email')}
    emp_label      = EMPRESA_LABELS.get(empresa, empresa)

    enviados, erros = 0, 0

    try:
        if config.get('smtp_tls', 1):
            srv = smtplib.SMTP(config['smtp_host'], int(config['smtp_port']), timeout=15)
            srv.starttls()
        else:
            srv = smtplib.SMTP_SSL(config['smtp_host'], int(config['smtp_port']), timeout=15)
        srv.login(config['smtp_usuario'], config['smtp_senha'])
    except Exception as e:
        flash(f"❌ Falha ao conectar no SMTP: {e}", "danger")
        return redirect(url_for('envio_mensagens'))

    from_name = config.get('smtp_from_name') or 'Cobranças'
    remetente = f"{from_name} <{config['smtp_usuario']}>"

    def _send_one(row, tmpl, col_venc, categoria):
        nonlocal enviados, erros
        cpf = str(row.get('CPF', '')).zfill(11) if row.get('CPF', '') else ''
        email_dest = row.get('E-mail') if pd.notna(row.get('E-mail', None)) else None
        if not email_dest or cpf in emails_hoje:
            return
        mensagem = _formatar_mensagem_wizard(row, tmpl, col_venc)
        assunto  = tmpl.get('assunto_email') or _assunto_padrao(categoria, emp_label)
        html_body = (
            "<html><body style='font-family:Arial,sans-serif;max-width:600px;"
            "margin:auto;padding:20px;color:#333'>"
            + mensagem.replace('\n', '<br>')
            + "</body></html>"
        )
        msg = MIMEMultipart('alternative')
        msg['From']    = remetente
        msg['To']      = email_dest
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        try:
            srv.sendmail(config['smtp_usuario'], [email_dest], msg.as_string())
            db.registrar_envio(cpf, empresa, 'email', tmpl['titulo'])
            enviados += 1
        except Exception as ex:
            _log(f"[{empresa}] ERRO e-mail {cpf}: {ex}")
            erros += 1

    for _, row in consolidado.iterrows():
        tmpl = _encontrar_template(int(row['Dias_Atraso']), templates_list)
        if tmpl:
            _send_one(row, tmpl, 'Ultimo_Vencimento', row['Categoria'])

    if avencer is not None and not avencer.empty:
        tmpl_av = next(
            (t for t in templates_list
             if t['categoria'] == 'A Vencer'
             or (t['dias_de'] is not None and t['dias_de'] < 0)),
            None
        )
        if tmpl_av:
            for _, row in avencer.iterrows():
                _send_one(row, tmpl_av, 'Proximo_Vencimento', 'A Vencer')

    try:
        srv.quit()
    except Exception:
        pass

    _log(f"[{empresa}] E-mails em lote: {enviados} enviados, {erros} erros")
    if enviados:
        flash(f"✅ {enviados} e-mail(s) enviado(s) com sucesso.", "success")
    if erros:
        flash(f"⚠️ {erros} e-mail(s) não puderam ser enviados. Verifique o log.", "warning")
    if not enviados and not erros:
        flash("Nenhum e-mail novo para enviar (todos já enviados hoje ou sem e-mail cadastrado).", "info")

    return redirect(url_for('envio_mensagens'))


# ---------------------------------------------------------------------------
# Fase H — Planilha CRM
# ---------------------------------------------------------------------------

@app.route('/crm/gerar-planilha', methods=['POST'])
def crm_gerar_planilha():
    empresa = get_empresa()
    consolidado, _, _, _ = _carregar_estado(empresa)
    if consolidado is None:
        flash("Consolide primeiro para gerar a planilha CRM.", "warning")
        return redirect(url_for('envio_mensagens'))

    templates_list = db.get_templates_completo(empresa)
    base_df        = db.carregar_base(empresa)

    CRM_PASTA.mkdir(parents=True, exist_ok=True)
    data_str = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

    try:
        nome_arq = proc.gerar_planilha_crm(
            consolidado, base_df, templates_list, CRM_PASTA, data_str, empresa
        )
        _log(f"[{empresa}] Planilha CRM gerada: {nome_arq}")
        os.startfile(str(CRM_PASTA))
        flash(f"✅ Planilha CRM gerada: {nome_arq.name} — pasta aberta automaticamente.", "success")
    except Exception as e:
        _log(f"[{empresa}] ERRO CRM: {e}")
        flash(f"Erro ao gerar planilha CRM: {e}", "danger")

    return redirect(url_for('envio_mensagens'))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("=" * 60)
    print("  Consolidador de Inadimplências — Multi-empresa")
    if PRIMEIRA_EXECUCAO:
        print(f"  ✓ Primeira execução: estrutura criada em {DATA_DIR}")
    print("  Acesse: http://localhost:5000")
    print("  Login padrão: luana / matine2026  (troque em 06_APP/.env)")
    print("=" * 60)
    app.run(debug=False, host='127.0.0.1', port=5000)
