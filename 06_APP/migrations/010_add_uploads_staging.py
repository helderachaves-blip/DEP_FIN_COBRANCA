"""010 - Tabela uploads_staging (EPIC-02 Onda 4 - upload stateless de arquivos).

Os arquivos importados (vencidos/avencer/alunos/pagos_cancelados) eram gravados em
disco (`C:\\MATINE\\uploads\\{empresa}\\{tipo}\\`) e detectados pela localizacao na hora
de consolidar. No servidor Linux o disco e efemero e nao compartilhado entre instancias,
entao os bytes do upload passam a descansar nesta tabela ate a consolidacao - sem tocar
o filesystem. O resultado processado continua indo para `estado_consolidacao` (Onda 3) e
para a base persistente `inadimplentes`; o bruto e substituido a cada novo upload.

A coluna `conteudo` guarda os bytes crus do arquivo (CSV/XLSX). PK = (empresa, tipo):
1 arquivo corrente por tipo por empresa. Cross-dialect: BLOB no SQLite vira BYTEA no
Postgres (ddl.blob()); `ON CONFLICT(empresa, tipo)` suportado em ambos.
"""
import ddl

version = 10
name = "add_uploads_staging"


def up(conn):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS uploads_staging (
            empresa       TEXT NOT NULL,
            tipo          TEXT NOT NULL,
            filename      TEXT NOT NULL,
            conteudo      {ddl.blob()} NOT NULL,
            atualizado_em TEXT NOT NULL {ddl.ts_default()},
            PRIMARY KEY (empresa, tipo)
        )
        """
    )


def down(conn):
    conn.execute("DROP TABLE IF EXISTS uploads_staging")
