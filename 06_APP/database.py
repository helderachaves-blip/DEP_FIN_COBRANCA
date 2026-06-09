"""
Operações SQLite — suporte multi-empresa (Fase D).
Todas as funções recebem o parâmetro `empresa`.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

DB_PATH = Path(r'C:\MATINE\banco\inadimplencia.db')

EMPRESAS = ('INEPROTEC', 'MATRICULAEAD')

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
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        # ── Criar tabelas base ──────────────────────────────────────────────
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS inadimplentes (
                cpf TEXT NOT NULL,
                aluno TEXT NOT NULL,
                telefone TEXT,
                email TEXT,
                qtd_boletos INTEGER,
                total REAL,
                ultimo_vencimento TEXT,
                dias_atraso INTEGER,
                categoria TEXT,
                status TEXT DEFAULT 'INADIMPLENTE',
                data_entrada TEXT,
                data_atualizacao TEXT
            );

            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT NOT NULL,
                titulo TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                ativo INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS historico_atualizacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                total_base INTEGER,
                novos INTEGER,
                saidos INTEGER,
                continuam INTEGER
            );
        """)

        # ── Migração Fase C: categorias A/B → novas nomenclaturas ──────────
        conn.execute(
            "UPDATE templates SET categoria='Inadimplentes Mês', titulo='Vencidos - 2 a 29 Dias' "
            "WHERE categoria='A' OR categoria='Régua'"
        )
        conn.execute(
            "UPDATE templates SET categoria='Acima 30 Dias', titulo='Cobranças Avançadas (Acima de 30 Dias)' "
            "WHERE categoria='B'"
        )
        conn.execute("UPDATE inadimplentes SET categoria='Inadimplentes Mês' WHERE categoria='A' OR categoria='Régua'")
        conn.execute("UPDATE inadimplentes SET categoria='Acima 30 Dias' WHERE categoria='B'")

        # ── Migração Fase D: adicionar coluna empresa ───────────────────────
        cols_i = [r[1] for r in conn.execute("PRAGMA table_info(inadimplentes)").fetchall()]
        if 'empresa' not in cols_i:
            # Recriar inadimplentes com PK composta (cpf, empresa)
            conn.executescript("""
                CREATE TABLE inadimplentes_v2 (
                    cpf               TEXT NOT NULL,
                    empresa           TEXT NOT NULL DEFAULT 'INEPROTEC',
                    aluno             TEXT NOT NULL,
                    telefone          TEXT,
                    email             TEXT,
                    qtd_boletos       INTEGER,
                    total             REAL,
                    ultimo_vencimento TEXT,
                    dias_atraso       INTEGER,
                    categoria         TEXT,
                    status            TEXT DEFAULT 'INADIMPLENTE',
                    data_entrada      TEXT,
                    data_atualizacao  TEXT,
                    PRIMARY KEY (cpf, empresa)
                );
                INSERT INTO inadimplentes_v2
                    (cpf, empresa, aluno, telefone, email, qtd_boletos, total,
                     ultimo_vencimento, dias_atraso, categoria, status,
                     data_entrada, data_atualizacao)
                SELECT cpf, 'INEPROTEC', aluno, telefone, email, qtd_boletos, total,
                       ultimo_vencimento, dias_atraso, categoria, status,
                       data_entrada, data_atualizacao
                FROM inadimplentes;
                DROP TABLE inadimplentes;
                ALTER TABLE inadimplentes_v2 RENAME TO inadimplentes;
            """)

        # ── Migração Fase E: adicionar coluna qtd_cobranca ─────────────────
        cols_post = [r[1] for r in conn.execute("PRAGMA table_info(inadimplentes)").fetchall()]
        if 'qtd_cobranca' not in cols_post:
            conn.execute(
                "ALTER TABLE inadimplentes ADD COLUMN qtd_cobranca INTEGER DEFAULT 0"
            )

        cols_t = [r[1] for r in conn.execute("PRAGMA table_info(templates)").fetchall()]
        if 'empresa' not in cols_t:
            conn.execute("ALTER TABLE templates ADD COLUMN empresa TEXT NOT NULL DEFAULT 'INEPROTEC'")

        # ── Migração Fase F: adicionar colunas dias_de e dias_ate ──────────
        cols_t2 = [r[1] for r in conn.execute("PRAGMA table_info(templates)").fetchall()]
        if 'dias_de' not in cols_t2:
            conn.execute("ALTER TABLE templates ADD COLUMN dias_de INTEGER")
        if 'dias_ate' not in cols_t2:
            conn.execute("ALTER TABLE templates ADD COLUMN dias_ate INTEGER")
        # Preencher dias padrão para templates já existentes
        conn.execute(
            "UPDATE templates SET dias_de=1, dias_ate=1 "
            "WHERE categoria='Novos Inadimplentes' AND dias_de IS NULL"
        )
        conn.execute(
            "UPDATE templates SET dias_de=2, dias_ate=29 "
            "WHERE categoria='Inadimplentes Mês' AND dias_de IS NULL"
        )
        conn.execute(
            "UPDATE templates SET dias_de=30 "
            "WHERE categoria='Acima 30 Dias' AND dias_de IS NULL"
        )

        cols_h = [r[1] for r in conn.execute("PRAGMA table_info(historico_atualizacoes)").fetchall()]
        if 'empresa' not in cols_h:
            conn.execute("ALTER TABLE historico_atualizacoes ADD COLUMN empresa TEXT NOT NULL DEFAULT 'INEPROTEC'")

        # ── Templates padrão por empresa ───────────────────────────────────
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

        # ── Migração Fase F/G: tabela envios + config_email ───────────────────
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS envios (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf            TEXT NOT NULL,
                empresa        TEXT NOT NULL,
                canal          TEXT NOT NULL,
                template_titulo TEXT,
                data_envio     TEXT NOT NULL,
                status         TEXT DEFAULT 'enviado'
            );
            CREATE TABLE IF NOT EXISTS config_email (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa        TEXT NOT NULL UNIQUE,
                smtp_host      TEXT DEFAULT '',
                smtp_port      INTEGER DEFAULT 587,
                smtp_usuario   TEXT DEFAULT '',
                smtp_senha     TEXT DEFAULT '',
                smtp_from_name TEXT DEFAULT '',
                smtp_tls       INTEGER DEFAULT 1
            );
        """)

        # Coluna assunto_email nos templates
        cols_t3 = [r[1] for r in conn.execute("PRAGMA table_info(templates)").fetchall()]
        if 'assunto_email' not in cols_t3:
            conn.execute("ALTER TABLE templates ADD COLUMN assunto_email TEXT")

        # Coluna tag_crm nos templates (Mudança 4 — planilha CRM)
        cols_t4 = [r[1] for r in conn.execute("PRAGMA table_info(templates)").fetchall()]
        if 'tag_crm' not in cols_t4:
            conn.execute("ALTER TABLE templates ADD COLUMN tag_crm TEXT")

        conn.commit()


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
        """, (empresa, host, port, usuario, senha, from_name, 1 if tls else 0))
        conn.commit()


def get_config_email(empresa: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM config_email WHERE empresa=?", (empresa,)
        ).fetchone()
    return dict(row) if row else None


def salvar_assunto_template(template_id: int, assunto: str, empresa: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE templates SET assunto_email=? WHERE id=? AND empresa=?",
            (assunto, template_id, empresa)
        )
        conn.commit()
