"""003 - Tabela envios (historico de envios por canal/empresa)."""
import ddl

version = 3
name = "add_envios"


def up(conn):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS envios (
            id              {ddl.pk_int()},
            cpf             TEXT NOT NULL,
            empresa         TEXT NOT NULL,
            canal           TEXT NOT NULL,
            template_titulo TEXT,
            data_envio      TEXT NOT NULL,
            status          TEXT DEFAULT 'enviado'
        )
        """
    )


def down(conn):
    conn.execute("DROP TABLE IF EXISTS envios")
