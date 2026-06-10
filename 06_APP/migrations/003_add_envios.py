"""003 - Tabela envios (historico de envios por canal/empresa)."""

version = 3
name = "add_envios"


def up(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS envios (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
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
