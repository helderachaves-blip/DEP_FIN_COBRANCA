"""
Operações de banco — suporte multi-empresa (Fase D).
Todas as funções recebem o parâmetro `empresa`.
Dialeto selecionado por DATABASE_URL: ausente → SQLite, presente → Postgres (Onda 1+).
"""

import importlib.util
import os
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

# ── Dialeto (EPIC-02 Onda 0) ─────────────────────────────────────────────────
# DATABASE_URL ausente  → SQLite (dev/testes/local)
# DATABASE_URL presente → Postgres (Render/produção)  — usado a partir da Onda 1
DATABASE_URL = os.environ.get('DATABASE_URL')
DIALECT = 'postgres' if DATABASE_URL else 'sqlite'

# Import protegido: psycopg só é necessário quando DIALECT == 'postgres'.
# Em dev/testes o pacote pode não estar instalado e o app continua funcionando.
try:
    import psycopg as _psycopg
    from psycopg.rows import dict_row as _pg_dict_row
    from psycopg.errors import UniqueViolation as _PGUniqueViolation
    import psycopg_pool as _psycopg_pool  # noqa: F401 — pool, usado na Onda 7
    _PSYCOPG_OK = True
except ImportError:
    _psycopg = _pg_dict_row = _PGUniqueViolation = _psycopg_pool = None
    _PSYCOPG_OK = False

# Erros de unicidade capturados em criar_usuario()
_IntegrityError = (sqlite3.IntegrityError,) + (
    (_PGUniqueViolation,) if _PGUniqueViolation else ()
)


class _PGConn:
    """Wraps psycopg Connection para espelhar a API sqlite3 usada neste módulo.

    - ? → %s antes de cada execute/executemany.
    - isolation_level = None mapeia para conn.autocommit = True (runner de migrations).
    - __exit__ faz commit/rollback + fecha conexão (evita leak em Postgres).
    """

    def __init__(self, pg_conn):
        self._conn = pg_conn
        self._closed = False

    @staticmethod
    def _sql(s: str) -> str:
        return s.replace('?', '%s')

    def execute(self, sql, params=()):
        return self._conn.execute(self._sql(sql), params)

    def executemany(self, sql, params_seq):
        return self._conn.executemany(self._sql(sql), list(params_seq))

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        if not self._closed:
            self._conn.close()
            self._closed = True

    @property
    def isolation_level(self):
        return None

    @isolation_level.setter
    def isolation_level(self, value):
        self._conn.autocommit = (value is None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            try:
                self._conn.rollback()
            except Exception:
                pass
        else:
            try:
                self._conn.commit()
            except Exception:
                pass
        self.close()
        return False

# Diretório de dados configurável por ambiente (default: C:\MATINE — produção
# inalterada). Os testes definem MATINE_DATA_DIR para um temp e nunca tocam o
# banco real. app.py lê a mesma variável para DATA_DIR.
DATA_DIR = Path(os.environ.get('MATINE_DATA_DIR', r'C:\MATINE'))
DB_PATH = DATA_DIR / 'banco' / 'inadimplencia.db'

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


def get_conn():
    """Retorna conexão SQLite ou Postgres conforme DIALECT (definido por DATABASE_URL).

    SQLite  → sqlite3.Connection com row_factory=Row e pragmas WAL+FK.
    Postgres → _PGConn wrapping psycopg.Connection com dict_row.
    """
    if DIALECT == 'sqlite':
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    if not _PSYCOPG_OK:
        raise RuntimeError(
            "psycopg não instalado. Instale: pip install 'psycopg[binary]' psycopg-pool"
        )
    return _PGConn(_psycopg.connect(DATABASE_URL, row_factory=_pg_dict_row))


def _table_exists(conn, name: str) -> bool:
    if DIALECT != 'sqlite':
        return False  # sem banco legado em Postgres — aplica todas as migrations
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
                    "INSERT INTO schema_migrations (version, name) VALUES (?, ?) "
                    "ON CONFLICT DO NOTHING",
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
            "VALUES ('Custom',?,?,?,?,?,?) RETURNING id",
            (titulo, conteudo, empresa, dias_de, dias_ate, tag_crm or None)
        )
        new_id = cur.fetchone()['id']
        conn.commit()
        return new_id


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
            "SELECT COUNT(*) AS cnt FROM inadimplentes WHERE empresa = ?", (empresa,)
        ).fetchone()['cnt']
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
            "SELECT COUNT(*) AS cnt FROM inadimplentes WHERE empresa = ?", (empresa,)
        ).fetchone()['cnt']
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


# ── Config WhatsApp / Google Drive (STORY-H-01) ──────────────────────────────
# A credencial da Service Account (JSON) é sensível e NÃO fica no banco. É gravada
# em DATA_DIR/secrets/gdrive_{empresa}.json (fora do git e do banco) e a coluna
# `gdrive_credentials` carrega apenas o marcador `[file]` — mesmo espírito da senha
# SMTP via keyring (STORY-01-04). O JSON da SA passa do limite do Windows Credential
# Store, por isso aqui usamos arquivo em vez de keyring.

SECRETS_DIR = DATA_DIR / 'secrets'
GDRIVE_CRED_MARKER = '[file]'


def _gdrive_cred_path(empresa: str) -> Path:
    return SECRETS_DIR / f'gdrive_{empresa}.json'


def gravar_gdrive_credentials(empresa: str, credentials_json: str) -> bool:
    """Grava o JSON da Service Account em DATA_DIR/secrets/. Retorna True em sucesso."""
    try:
        SECRETS_DIR.mkdir(parents=True, exist_ok=True)
        _gdrive_cred_path(empresa).write_text(credentials_json, encoding='utf-8')
        return True
    except Exception as e:  # pragma: no cover - falha de filesystem
        print(f"[gdrive] falha ao gravar credencial de {empresa}: {e}")
        return False


def get_gdrive_credentials_path(empresa: str) -> Path | None:
    """Caminho do JSON da Service Account, ou None se ainda não configurado."""
    p = _gdrive_cred_path(empresa)
    return p if p.exists() else None


def tem_gdrive_credentials(empresa: str) -> bool:
    return get_gdrive_credentials_path(empresa) is not None


def salvar_config_whatsapp(empresa: str, folder_id: str, filename_template: str,
                           kommo_webhook_url: str, kommo_pipeline_id: str,
                           exportar_automatico: bool,
                           credentials_json: str | None = None,
                           auth_method: str = 'service_account'):
    """Salva (upsert) a config WhatsApp da empresa.

    `credentials_json` só é gravado quando vem preenchido — campo vazio preserva a
    credencial atual (espelha o comportamento da senha SMTP). A coluna recebe o
    marcador `[file]` quando há credencial em disco.
    """
    if credentials_json:
        gravar_gdrive_credentials(empresa, credentials_json)
    cred_marker = GDRIVE_CRED_MARKER if tem_gdrive_credentials(empresa) else None
    with get_conn() as conn:
        now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute("""
            INSERT INTO config_whatsapp
                (empresa, gdrive_auth_method, gdrive_credentials, gdrive_folder_id,
                 gdrive_filename_template, kommo_webhook_url, kommo_pipeline_id,
                 exportar_automatico, atualizado_em)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(empresa) DO UPDATE SET
                gdrive_auth_method=excluded.gdrive_auth_method,
                gdrive_credentials=excluded.gdrive_credentials,
                gdrive_folder_id=excluded.gdrive_folder_id,
                gdrive_filename_template=excluded.gdrive_filename_template,
                kommo_webhook_url=excluded.kommo_webhook_url,
                kommo_pipeline_id=excluded.kommo_pipeline_id,
                exportar_automatico=excluded.exportar_automatico,
                atualizado_em=excluded.atualizado_em
        """, (empresa, auth_method, cred_marker, folder_id, filename_template,
              kommo_webhook_url, kommo_pipeline_id, 1 if exportar_automatico else 0, now_ts))
        conn.commit()


def get_config_whatsapp(empresa: str) -> dict | None:
    """Config WhatsApp da empresa. A credencial nunca é devolvida em texto: apenas
    o flag `tem_credenciais` e o caminho do arquivo (`credentials_path`)."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM config_whatsapp WHERE empresa=?", (empresa,)
        ).fetchone()
    if not row:
        return None
    cfg = dict(row)
    cfg.pop('gdrive_credentials', None)  # nunca expor o marcador/conteúdo
    cfg['tem_credenciais'] = tem_gdrive_credentials(empresa)
    cred = get_gdrive_credentials_path(empresa)
    cfg['credentials_path'] = str(cred) if cred else None
    return cfg


def salvar_assunto_template(template_id: int, assunto: str, empresa: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE templates SET assunto_email=? WHERE id=? AND empresa=?",
            (assunto, template_id, empresa)
        )
        conn.commit()


# ── Usuários (autenticação multi-usuário, migration 007) ─────────────────────

def seed_usuario_admin(usuario: str, nome: str, senha_hash: str) -> bool:
    """Cria o primeiro admin se a tabela `usuarios` estiver vazia. Idempotente.

    Bootstrap da autenticação: na primeira vez, o usuário/senha do .env vira o
    admin inicial — assim ninguém fica trancado para fora ao migrar do modelo
    de usuário único para multi-usuário. Retorna True se criou.
    """
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) AS cnt FROM usuarios").fetchone()['cnt']
        if total == 0:
            conn.execute(
                "INSERT INTO usuarios (usuario, nome, senha_hash, is_admin) VALUES (?,?,?,1)",
                (usuario, nome or usuario, senha_hash)
            )
            conn.commit()
            return True
    return False


def get_usuario_por_login(usuario: str) -> dict | None:
    """Usuário ativo pelo login (para autenticar). None se não existe/inativo."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND ativo = 1", (usuario,)
        ).fetchone()
    return dict(row) if row else None


def get_usuario_por_id(user_id) -> dict | None:
    """Usuário ativo pelo id (para o user_loader do Flask-Login)."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE id = ? AND ativo = 1", (user_id,)
        ).fetchone()
    return dict(row) if row else None


def listar_usuarios() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, usuario, nome, is_admin, ativo, criado_em "
            "FROM usuarios ORDER BY is_admin DESC, usuario ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def criar_usuario(usuario: str, nome: str, senha_hash: str,
                  is_admin: bool = False) -> tuple[bool, str]:
    """Cria um usuário. Retorna (ok, mensagem_de_erro)."""
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO usuarios (usuario, nome, senha_hash, is_admin) VALUES (?,?,?,?)",
                (usuario, nome, senha_hash, 1 if is_admin else 0)
            )
            conn.commit()
        return True, ""
    except _IntegrityError:
        return False, f"Já existe um usuário com o login '{usuario}'."


def atualizar_senha_usuario(user_id, senha_hash: str):
    with get_conn() as conn:
        conn.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", (senha_hash, user_id))
        conn.commit()


def atualizar_nome_usuario(user_id, nome: str):
    """Atualiza o nome de exibição. Vazio → o login passa a ser exibido (fallback no app)."""
    with get_conn() as conn:
        conn.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (nome, user_id))
        conn.commit()


def set_usuario_admin(user_id, is_admin: bool):
    with get_conn() as conn:
        conn.execute("UPDATE usuarios SET is_admin = ? WHERE id = ?",
                     (1 if is_admin else 0, user_id))
        conn.commit()


def remover_usuario(user_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
        conn.commit()


def is_ultimo_admin(user_id) -> bool:
    """True se este usuário é admin e é o único admin ativo (proteção anti-lockout)."""
    with get_conn() as conn:
        row = conn.execute("SELECT is_admin FROM usuarios WHERE id = ?", (user_id,)).fetchone()
        if not row or not row['is_admin']:
            return False
        admins = conn.execute(
            "SELECT COUNT(*) AS cnt FROM usuarios WHERE is_admin = 1 AND ativo = 1"
        ).fetchone()['cnt']
    return admins <= 1


# ── Estado de consolidação (EPIC-02 Onda 3 — blob no banco, não mais pickle em disco) ─
# O estado da sessão de consolidação por empresa (DataFrames + stats) é serializado
# com pickle em app.py e persistido aqui como blob. Tira o app da dependência do disco
# local — pré-requisito para rodar stateless na nuvem. Um estado por empresa (PK).

def salvar_estado_blob(empresa: str, payload: bytes):
    """Grava (ou substitui) o estado serializado da empresa."""
    now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO estado_consolidacao (empresa, payload, atualizado_em) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT(empresa) DO UPDATE SET "
            "    payload=excluded.payload, atualizado_em=excluded.atualizado_em",
            (empresa, payload, now_ts)
        )
        conn.commit()


def carregar_estado_blob(empresa: str) -> bytes | None:
    """Lê o estado serializado da empresa. None se não houver."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT payload FROM estado_consolidacao WHERE empresa = ?", (empresa,)
        ).fetchone()
    if not row:
        return None
    payload = row['payload']
    # sqlite3 entrega BLOB como bytes; normaliza memoryview (psycopg/BYTEA na nuvem).
    return bytes(payload) if payload is not None else None


def limpar_estado_blob(empresa: str):
    """Remove o estado da empresa (equivalente ao antigo unlink do .pkl)."""
    with get_conn() as conn:
        conn.execute("DELETE FROM estado_consolidacao WHERE empresa = ?", (empresa,))
        conn.commit()


def estado_existe(empresa: str) -> bool:
    """Existe estado para a empresa? Check leve (não carrega o blob) — usado a cada request."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM estado_consolidacao WHERE empresa = ?", (empresa,)
        ).fetchone()
    return row is not None


# ---------------------------------------------------------------------------
# Uploads em staging (EPIC-02 Onda 4) — bytes do arquivo importado descansam no
# banco até a consolidação, no lugar do disco local (uploads/{empresa}/{tipo}/).
# Um arquivo corrente por (empresa, tipo); substituído a cada novo upload.

# Tipos de arquivo aceitos em staging (mesmos detectados por pasta antes).
TIPOS_UPLOAD = ('vencidos', 'avencer', 'alunos', 'pagos_cancelados')


def salvar_upload_staging(empresa: str, tipo: str, filename: str, conteudo: bytes):
    """Grava (ou substitui) os bytes do arquivo importado para a empresa/tipo."""
    now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO uploads_staging (empresa, tipo, filename, conteudo, atualizado_em) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(empresa, tipo) DO UPDATE SET "
            "    filename=excluded.filename, conteudo=excluded.conteudo, "
            "    atualizado_em=excluded.atualizado_em",
            (empresa, tipo, filename, conteudo, now_ts)
        )
        conn.commit()


def carregar_upload_staging(empresa: str, tipo: str) -> tuple[str, bytes] | None:
    """Lê (filename, bytes) do arquivo em staging. None se não houver."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT filename, conteudo FROM uploads_staging WHERE empresa = ? AND tipo = ?",
            (empresa, tipo)
        ).fetchone()
    if not row:
        return None
    conteudo = row['conteudo']
    # sqlite3 entrega BLOB como bytes; normaliza memoryview (psycopg/BYTEA na nuvem).
    return row['filename'], (bytes(conteudo) if conteudo is not None else b'')


def limpar_upload_staging(empresa: str, tipo: str | None = None):
    """Remove o(s) arquivo(s) em staging da empresa (um tipo, ou todos se tipo=None)."""
    with get_conn() as conn:
        if tipo is None:
            conn.execute("DELETE FROM uploads_staging WHERE empresa = ?", (empresa,))
        else:
            conn.execute(
                "DELETE FROM uploads_staging WHERE empresa = ? AND tipo = ?",
                (empresa, tipo)
            )
        conn.commit()


def status_uploads_staging(empresa: str) -> dict[str, str]:
    """Retorna {tipo: filename} dos arquivos atualmente em staging (para a UI de presença)."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT tipo, filename FROM uploads_staging WHERE empresa = ?", (empresa,)
        ).fetchall()
    return {r['tipo']: r['filename'] for r in rows}
