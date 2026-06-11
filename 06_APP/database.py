"""
Operações SQLite — suporte multi-empresa (Fase D).
Todas as funções recebem o parâmetro `empresa`.
"""

import importlib.util
import os
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

DB_PATH = Path(r'C:\MATINE\banco\inadimplencia.db')

EMPRESAS = ('INEPROTEC', 'MATRICULAEAD')

# ── Senha SMTP segura via keyring (STORY-01-04) ──────────────────────────────
# A senha SMTP nunca fica em texto plano no banco. É guardada no Windows Credential
# Store (keyring). A coluna `config_email.smtp_senha` carrega apenas um marcador.
# Import protegido: se o keyring não estiver disponível no ambiente, o sistema
# continua funcionando via fallback em variável de ambiente.
try:
    import keyring as _keyring
    _KEYRING_OK = True
except Exception:  # pragma: no cover - ambiente sem keyring
    _keyring = None
    _KEYRING_OK = False

KEYRING_SERVICE = "matine-smtp"
SENHA_MARKER = "[keyring]"


def _env_senha(empresa: str) -> str | None:
    """Fallback de rollback: SMTP_INEPROTEC_SENHA / SMTP_MATRICULAEAD_SENHA."""
    return os.environ.get(f"SMTP_{empresa}_SENHA") or None


def _gravar_senha_smtp(empresa: str, senha: str) -> bool:
    """Grava a senha no keyring. Retorna False (com log) se o keyring falhar."""
    if _KEYRING_OK:
        try:
            _keyring.set_password(KEYRING_SERVICE, empresa, senha)
            return True
        except Exception as e:  # pragma: no cover
            print(f"[smtp] keyring indisponível na escrita: {e}")
    print(f"[smtp] Keyring não disponível. "
          f"Configure SMTP_{empresa}_SENHA como variável de ambiente.")
    return False


def _ler_senha_smtp(empresa: str, col_fallback: str | None = None) -> str | None:
    """Lê a senha de forma segura: keyring → variável de ambiente → coluna (legado).

    O fallback de coluna só é usado se o keyring/env falharem e a coluna ainda tiver
    uma senha real (não vazia e não o marcador) — evita regressão em ambientes onde o
    keyring ainda não migrou. Retorna None se nenhuma fonte tiver a senha.
    """
    if _KEYRING_OK:
        try:
            v = _keyring.get_password(KEYRING_SERVICE, empresa)
            if v:
                return v
        except Exception as e:  # pragma: no cover
            print(f"[smtp] keyring indisponível na leitura: {e}")
    env = _env_senha(empresa)
    if env:
        return env
    if col_fallback and col_fallback not in ('', SENHA_MARKER):
        return col_fallback
    return None


def migrar_senhas_smtp():
    """Move senhas SMTP em texto plano (legado) para o keyring e grava o marcador.

    Idempotente: linhas já marcadas com SENHA_MARKER ou vazias são ignoradas. Se o
    keyring falhar, a senha permanece na coluna (para não quebrar envios) e fica um aviso.
    """
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT empresa, smtp_senha FROM config_email "
            "WHERE smtp_senha IS NOT NULL AND smtp_senha NOT IN ('', ?)",
            (SENHA_MARKER,)
        ).fetchall()
        for r in rows:
            empresa, senha_plana = r['empresa'], r['smtp_senha']
            if _gravar_senha_smtp(empresa, senha_plana):
                conn.execute(
                    "UPDATE config_email SET smtp_senha=? WHERE empresa=?",
                    (SENHA_MARKER, empresa)
                )
                print(f"[smtp] senha de {empresa} migrada para o keyring")
            else:
                print(f"[smtp] AVISO: keyring indisponível; senha de {empresa} permanece no banco")
        conn.commit()

# Diretório de migrations (STORY-01-05). Carregamos o runner por caminho para não
# depender de o pacote `migrations` estar no sys.path (funciona de qualquer cwd).
_APP_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = _APP_DIR / 'migrations'
_runner_spec = importlib.util.spec_from_file_location(
    'migrations_runner', MIGRATIONS_DIR / 'runner.py'
)
runner = importlib.util.module_from_spec(_runner_spec)
_runner_spec.loader.exec_module(runner)

# Migrations que apenas CRIAM schema. Num banco legado (criado pelo init_db antigo, que já
# produzia o schema final) elas são marcadas como aplicadas sem re-executar. As migrations
# realmente novas (005 índices, 006 WAL) rodam normalmente.
_BASELINE_LEGADO = [
    (1, 'initial_schema'),
    (2, 'add_historico'),
    (3, 'add_envios'),
    (4, 'add_config_email'),
]

TEMPLATES_PADRAO = {
    'INEPROTEC': [
        {
            'categoria': 'A Vencer',
            'titulo': 'Lembrete de Vencimento (Dia -1)',
            'dias_de': None,
            'dias_ate': None,
            'conteudo': (
                "Olá, {TRATAMENTO} {NOME}. Tudo bem?\n"
                "Somos do setor financeiro da Ineprotec.\n"
                "Seu boleto com vencimento em {DATA_VENCIMENTO} vence amanhã.\n"
                "Para sua comodidade, segue o link de pagamento: {LINK_PAGAMENTO}\n"
                "Qualquer dúvida estamos à disposição!"
            ),
        },
        {
            'categoria': 'Novos Inadimplentes',
            'titulo': 'Novos Inadimplentes (1 Dia de Atraso)',
            'dias_de': 1,
            'dias_ate': 1,
            'conteudo': (
                "Olá, {TRATAMENTO} {NOME}. Tudo bem?\n"
                "Somos do setor financeiro da Ineprotec.\n"
                "Identificamos que o boleto do seu Curso Técnico com vencimento em {DATA_VENCIMENTO} "
                "ainda consta em aberto em nosso sistema.\n"
                "Se já realizou o pagamento, favor desconsiderar a mensagem!\n"
                "Qualquer dúvida estamos à disposição!"
            ),
        },
        {
            'categoria': 'Inadimplentes Mês',
            'titulo': 'Vencidos - 2 a 29 Dias',
            'dias_de': 2,
            'dias_ate': 29,
            'conteudo': (
                "Olá, {TRATAMENTO} {NOME}. Tudo bem?\n"
                "Somos do setor financeiro da Ineprotec.\n"
                "Para sua maior comodidade estamos enviando o boleto referente ao seu Curso Técnico, "
                "com vencimento em {DATA_VENCIMENTO}.\n"
                "Se já realizou o pagamento, favor desconsiderar a mensagem!\n"
                "Qualquer dúvida estamos à disposição!"
            ),
        },
        {
            'categoria': 'Acima 30 Dias',
            'titulo': 'Cobranças Avançadas (Acima de 30 Dias)',
            'dias_de': 30,
            'dias_ate': None,
            'conteudo': (
                "Olá, {TRATAMENTO} {NOME}. Tudo bem?\n"
                "Somos do setor financeiro da Ineprotec. "
                "O motivo do meu contato é referente às parcelas em aberto do seu Curso Técnico. "
                "Tem interesse em retornar ao curso?"
            ),
        },
    ],
    'MATRICULAEAD': [
        {
            'categoria': 'A Vencer',
            'titulo': 'Lembrete de Vencimento (Dia -1)',
            'dias_de': None,
            'dias_ate': None,
            'conteudo': (
                "Olá, {TRATAMENTO} {NOME}. Tudo bem?\n"
                "Somos do setor financeiro do Matrícula EaD.\n"
                "Seu boleto com vencimento em {DATA_VENCIMENTO} vence amanhã.\n"
                "Para sua comodidade, segue o link de pagamento: {LINK_PAGAMENTO}\n"
                "Qualquer dúvida estamos à disposição!"
            ),
        },
        {
            'categoria': 'Novos Inadimplentes',
            'titulo': 'Novos Inadimplentes (1 Dia de Atraso)',
            'dias_de': 1,
            'dias_ate': 1,
            'conteudo': (
                "Olá, {TRATAMENTO} {NOME}. Tudo bem?\n"
                "Somos do setor financeiro do Matrícula EaD.\n"
                "Identificamos que o boleto do seu Curso Técnico com vencimento em {DATA_VENCIMENTO} "
                "ainda consta em aberto em nosso sistema.\n"
                "Se já realizou o pagamento, favor desconsiderar a mensagem!\n"
                "Qualquer dúvida estamos à disposição!"
            ),
        },
        {
            'categoria': 'Inadimplentes Mês',
            'titulo': 'Vencidos - 2 a 29 Dias',
            'dias_de': 2,
            'dias_ate': 29,
            'conteudo': (
                "Olá, {TRATAMENTO} {NOME}. Tudo bem?\n"
                "Somos do setor financeiro do Matrícula EaD.\n"
                "Para sua maior comodidade estamos enviando o boleto referente ao seu Curso Técnico, "
                "com vencimento em {DATA_VENCIMENTO}.\n"
                "Se já realizou o pagamento, favor desconsiderar a mensagem!\n"
                "Qualquer dúvida estamos à disposição!"
            ),
        },
        {
            'categoria': 'Acima 30 Dias',
            'titulo': 'Cobranças Avançadas (Acima de 30 Dias)',
            'dias_de': 30,
            'dias_ate': None,
            'conteudo': (
                "Olá, {TRATAMENTO} {NOME}. Tudo bem?\n"
                "Somos do setor financeiro do Matrícula EaD. "
                "O motivo do meu contato é referente às parcelas em aberto do seu Curso Técnico. "
                "Tem interesse em retornar ao curso?"
            ),
        },
    ],
}


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Pragmas por conexão (STORY-01-05 AC-05). Executados em conexão recém-aberta,
    # antes de qualquer transação:
    #  - WAL: leituras concorrentes durante escritas (persistente no arquivo do banco)
    #  - foreign_keys=ON: por-conexão; prepara o banco para constraints formais
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _table_exists(conn, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (name,)
    ).fetchone() is not None


def _seed_templates_padrao(conn):
    """Garante os templates padrão por empresa (idempotente — só insere o que falta)."""
    for emp, lista in TEMPLATES_PADRAO.items():
        for t in lista:
            existe = conn.execute(
                "SELECT id FROM templates WHERE categoria = ? AND empresa = ?",
                (t['categoria'], emp)
            ).fetchone()
            if not existe:
                conn.execute(
                    "INSERT INTO templates (categoria, titulo, conteudo, empresa, dias_de, dias_ate) "
                    "VALUES (?,?,?,?,?,?)",
                    (t['categoria'], t['titulo'], t['conteudo'], emp, t.get('dias_de'), t.get('dias_ate'))
                )


def init_db():
    """Inicializa/atualiza o banco via migrations versionadas (STORY-01-05).

    Fluxo: (1) garante schema_migrations; (2) detecta banco legado e marca as migrations
    de criação como aplicadas; (3) aplica apenas as migrations pendentes em ordem;
    (4) garante os templates padrão (idempotente).
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    conn.isolation_level = None  # autocommit: o runner controla as transações manualmente
    try:
        runner.ensure_migrations_table(conn)

        # Banco legado: tem schema (criado pelo init_db antigo) mas nunca foi versionado.
        # Marca 001-004 como aplicadas sem re-executar; 005/006 rodam normalmente.
        if not runner.applied_versions(conn) and _table_exists(conn, 'inadimplentes'):
            for v, n in _BASELINE_LEGADO:
                conn.execute(
                    "INSERT OR IGNORE INTO schema_migrations (version, name) VALUES (?, ?)",
                    (v, n)
                )
            print("[db] banco legado detectado - migrations 001-004 marcadas como aplicadas")

        aplicadas = runner.apply_pending(conn, MIGRATIONS_DIR, log=print)
        _seed_templates_padrao(conn)

        if aplicadas:
            print(f"[db] {len(aplicadas)} migration(s) aplicada(s) com sucesso: {aplicadas}")
        else:
            print("[db] schema na versao mais recente - nenhuma migration pendente")
    finally:
        conn.close()

    # Migração de segurança (STORY-01-04): move senhas SMTP em texto plano para o keyring.
    # Roda em conexão própria, após o fechamento da conexão das migrations.
    migrar_senhas_smtp()


# ── Templates ───────────────────────────────────────────────────────────────

def get_templates(empresa: str) -> dict[str, str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT categoria, conteudo FROM templates WHERE empresa = ? AND ativo = 1",
            (empresa,)
        ).fetchall()
    return {r['categoria']: r['conteudo'] for r in rows}


def get_templates_completo(empresa: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM templates WHERE empresa = ?
               ORDER BY CASE WHEN dias_de IS NULL THEN -999999 ELSE dias_de END ASC, id ASC""",
            (empresa,)
        ).fetchall()
    return [dict(r) for r in rows]


def criar_template(titulo: str, conteudo: str, empresa: str,
                   dias_de: int | None, dias_ate: int | None,
                   tag_crm: str = '') -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO templates (categoria, titulo, conteudo, empresa, dias_de, dias_ate, tag_crm) "
            "VALUES ('Custom',?,?,?,?,?,?)",
            (titulo, conteudo, empresa, dias_de, dias_ate, tag_crm or None)
        )
        conn.commit()
        return cur.lastrowid


def excluir_template(template_id: int, empresa: str):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM templates WHERE id = ? AND empresa = ?",
            (template_id, empresa)
        )
        conn.commit()


def incrementar_cobrancas(cpfs: list, empresa: str):
    if not cpfs:
        return
    with get_conn() as conn:
        conn.executemany(
            "UPDATE inadimplentes SET qtd_cobranca = COALESCE(qtd_cobranca, 0) + 1 "
            "WHERE cpf = ? AND empresa = ?",
            [(cpf, empresa) for cpf in cpfs]
        )
        conn.commit()


def salvar_template(template_id: int, titulo: str, conteudo: str, empresa: str,
                    dias_de: int | None = None, dias_ate: int | None = None,
                    tag_crm: str = ''):
    with get_conn() as conn:
        conn.execute(
            "UPDATE templates SET titulo=?, conteudo=?, dias_de=?, dias_ate=?, tag_crm=? "
            "WHERE id=? AND empresa=?",
            (titulo, conteudo, dias_de, dias_ate, tag_crm or None, template_id, empresa)
        )
        conn.commit()


# ── Base de inadimplentes ───────────────────────────────────────────────────

def carregar_base(empresa: str) -> pd.DataFrame:
    with get_conn() as conn:
        df = pd.read_sql(
            "SELECT * FROM inadimplentes WHERE empresa = ? ORDER BY aluno",
            conn, params=(empresa,)
        )
    return df


def salvar_base(novo_consolidado: pd.DataFrame, empresa: str,
                cpfs_avencer: set | None = None,
                cpfs_pagos: set | None = None,
                cpfs_cancelados: set | None = None) -> dict:
    hoje  = datetime.now().strftime('%d/%m/%Y')
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    with get_conn() as conn:
        base_atual = pd.read_sql(
            "SELECT cpf, data_entrada, status FROM inadimplentes WHERE empresa = ?",
            conn, params=(empresa,)
        )

    cpfs_base  = set(base_atual['cpf']) if not base_atual.empty else set()
    cpfs_novo  = set(novo_consolidado['CPF'].astype(str).str.zfill(11))
    novos_cpfs    = cpfs_novo - cpfs_base
    saidos_cpfs   = cpfs_base - cpfs_novo
    continuam_cpfs = cpfs_base & cpfs_novo

    entrada_map = dict(zip(base_atual['cpf'], base_atual['data_entrada'])) if not base_atual.empty else {}
    status_map  = dict(zip(base_atual['cpf'], base_atual['status']))       if not base_atual.empty else {}

    saidos_renegociados, saidos_quitados, saidos_cancelados = [], [], []

    with get_conn() as conn:
        for cpf in saidos_cpfs:
            if cpfs_pagos is not None and cpf in cpfs_pagos:
                # Confirmado como pago pelo relatório Synapta
                conn.execute(
                    "UPDATE inadimplentes SET status='QUITADO', data_atualizacao=? "
                    "WHERE cpf=? AND empresa=?",
                    (agora, cpf, empresa)
                )
                saidos_quitados.append(cpf)
            elif cpfs_cancelados is not None and cpf in cpfs_cancelados:
                # Confirmado como cancelado pelo relatório Synapta
                conn.execute(
                    "UPDATE inadimplentes SET status='CANCELADO', data_atualizacao=? "
                    "WHERE cpf=? AND empresa=?",
                    (agora, cpf, empresa)
                )
                saidos_cancelados.append(cpf)
            elif cpfs_avencer and cpf in cpfs_avencer:
                # Saiu dos vencidos mas tem boleto a vencer → renegociação
                conn.execute(
                    "UPDATE inadimplentes SET status='RENEGOCIADO', data_atualizacao=? "
                    "WHERE cpf=? AND empresa=?",
                    (agora, cpf, empresa)
                )
                saidos_renegociados.append(cpf)
            elif cpfs_pagos is None:
                # Sem relatório de pagos/cancelados: usa lógica de ausência (legado)
                conn.execute(
                    "UPDATE inadimplentes SET status='QUITADO', data_atualizacao=? "
                    "WHERE cpf=? AND empresa=?",
                    (agora, cpf, empresa)
                )
                saidos_quitados.append(cpf)
            # else: relatório fornecido mas CPF não encontrado → situação indefinida, mantém status atual

        for _, row in novo_consolidado.iterrows():
            cpf          = str(row['CPF']).zfill(11)
            data_entrada = entrada_map.get(cpf, hoje)
            status       = status_map.get(cpf, 'INADIMPLENTE')
            venc = (row['Ultimo_Vencimento'].strftime('%d/%m/%Y')
                    if hasattr(row['Ultimo_Vencimento'], 'strftime')
                    else str(row['Ultimo_Vencimento']))
            conn.execute("""
                INSERT INTO inadimplentes
                    (cpf, empresa, aluno, telefone, email, qtd_boletos, total,
                     ultimo_vencimento, dias_atraso, categoria, status,
                     data_entrada, data_atualizacao)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(cpf, empresa) DO UPDATE SET
                    aluno             = excluded.aluno,
                    telefone          = excluded.telefone,
                    email             = excluded.email,
                    qtd_boletos       = excluded.qtd_boletos,
                    total             = excluded.total,
                    ultimo_vencimento = excluded.ultimo_vencimento,
                    dias_atraso       = excluded.dias_atraso,
                    categoria         = excluded.categoria,
                    data_atualizacao  = excluded.data_atualizacao
            """, (
                cpf, empresa, row['Aluno'],
                row.get('Telefone') if pd.notna(row.get('Telefone', None)) else None,
                row.get('E-mail')   if pd.notna(row.get('E-mail',   None)) else None,
                int(row['Qtd_Boletos']),
                float(row['Total']),
                venc,
                int(row['Dias_Atraso']),
                row['Categoria'],
                status,
                data_entrada,
                agora,
            ))

        total_base = conn.execute(
            "SELECT COUNT(*) FROM inadimplentes WHERE empresa = ?", (empresa,)
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO historico_atualizacoes (data, total_base, novos, saidos, continuam, empresa) "
            "VALUES (?,?,?,?,?,?)",
            (agora, total_base, len(novos_cpfs), len(saidos_cpfs), len(continuam_cpfs), empresa)
        )
        conn.commit()

    return {
        'novos':               sorted(novos_cpfs),
        'saidos':              sorted(saidos_cpfs),
        'saidos_renegociados': sorted(saidos_renegociados),
        'saidos_quitados':     sorted(saidos_quitados),
        'saidos_cancelados':   sorted(saidos_cancelados),
        'continuam':           len(continuam_cpfs),
        'total':               total_base,
    }


def limpar_base(empresa: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM inadimplentes WHERE empresa = ?", (empresa,))
        conn.execute("DELETE FROM historico_atualizacoes WHERE empresa = ?", (empresa,))
        conn.commit()


def atualizar_status_aluno(cpf: str, status: str, empresa: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE inadimplentes SET status = ?, data_atualizacao = ? WHERE cpf = ? AND empresa = ?",
            (status, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), cpf, empresa)
        )
        conn.commit()


def status_base(empresa: str) -> dict:
    with get_conn() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM inadimplentes WHERE empresa = ?", (empresa,)
        ).fetchone()[0]
        ult = conn.execute(
            "SELECT data FROM historico_atualizacoes WHERE empresa = ? ORDER BY id DESC LIMIT 1",
            (empresa,)
        ).fetchone()
    return {
        'total': total,
        'ultima_atualizacao': ult['data'] if ult else None,
    }


# ── Envios (Fases F/G) ───────────────────────────────────────────────────────

def registrar_envio(cpf: str, empresa: str, canal: str, template_titulo: str = None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO envios (cpf, empresa, canal, template_titulo, data_envio) VALUES (?,?,?,?,?)",
            (cpf, empresa, canal, template_titulo,
             datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        )
        conn.commit()


def get_envios_hoje(empresa: str, canal: str = None) -> list[dict]:
    hoje = datetime.now().strftime('%d/%m/%Y')
    with get_conn() as conn:
        if canal:
            rows = conn.execute(
                "SELECT * FROM envios WHERE empresa=? AND canal=? AND data_envio LIKE ?",
                (empresa, canal, f"{hoje}%")
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM envios WHERE empresa=? AND data_envio LIKE ?",
                (empresa, f"{hoje}%")
            ).fetchall()
    return [dict(r) for r in rows]


# ── Config e-mail (Fase G) ───────────────────────────────────────────────────

def salvar_config_email(empresa: str, host: str, port: int, usuario: str,
                        senha: str, from_name: str, tls: bool):
    # Senha: gravada no keyring apenas se veio preenchida. Campo vazio preserva a senha
    # atual (AC-04). A coluna nunca recebe a senha real — apenas o marcador.
    if senha:
        _gravar_senha_smtp(empresa, senha)
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO config_email
                (empresa, smtp_host, smtp_port, smtp_usuario, smtp_senha, smtp_from_name, smtp_tls)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(empresa) DO UPDATE SET
                smtp_host=excluded.smtp_host,
                smtp_port=excluded.smtp_port,
                smtp_usuario=excluded.smtp_usuario,
                smtp_senha=excluded.smtp_senha,
                smtp_from_name=excluded.smtp_from_name,
                smtp_tls=excluded.smtp_tls
        """, (empresa, host, port, usuario, SENHA_MARKER, from_name, 1 if tls else 0))
        conn.commit()


def get_config_email(empresa: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM config_email WHERE empresa=?", (empresa,)
        ).fetchone()
    if not row:
        return None
    cfg = dict(row)
    # Senha lida do keyring (com fallback env/coluna-legado). None se não configurada.
    cfg['smtp_senha'] = _ler_senha_smtp(empresa, cfg.get('smtp_senha'))
    return cfg


def salvar_assunto_template(template_id: int, assunto: str, empresa: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE templates SET assunto_email=? WHERE id=? AND empresa=?",
            (assunto, template_id, empresa)
        )
        conn.commit()
