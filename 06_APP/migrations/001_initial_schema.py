"""001 - Schema base: inadimplentes + templates (forma final, multi-empresa)."""
import ddl

version = 1
name = "initial_schema"


def up(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS inadimplentes (
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
            qtd_cobranca      INTEGER DEFAULT 0,
            PRIMARY KEY (cpf, empresa)
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS templates (
            id            {ddl.pk_int()},
            categoria     TEXT NOT NULL,
            titulo        TEXT NOT NULL,
            conteudo      TEXT NOT NULL,
            ativo         INTEGER DEFAULT 1,
            empresa       TEXT NOT NULL DEFAULT 'INEPROTEC',
            dias_de       INTEGER,
            dias_ate      INTEGER,
            assunto_email TEXT,
            tag_crm       TEXT
        )
        """
    )


def down(conn):
    conn.execute("DROP TABLE IF EXISTS templates")
    conn.execute("DROP TABLE IF EXISTS inadimplentes")
