"""004 - Tabela config_email (SMTP por empresa)."""
import ddl

version = 4
name = "add_config_email"


def up(conn):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS config_email (
            id             {ddl.pk_int()},
            empresa        TEXT NOT NULL UNIQUE,
            smtp_host      TEXT DEFAULT '',
            smtp_port      INTEGER DEFAULT 587,
            smtp_usuario   TEXT DEFAULT '',
            smtp_senha     TEXT DEFAULT '',
            smtp_from_name TEXT DEFAULT '',
            smtp_tls       INTEGER DEFAULT 1
        )
        """
    )


def down(conn):
    conn.execute("DROP TABLE IF EXISTS config_email")
