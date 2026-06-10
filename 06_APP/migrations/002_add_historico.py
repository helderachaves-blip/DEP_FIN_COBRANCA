"""002 - Tabela historico_atualizacoes (forma final, com empresa)."""

version = 2
name = "add_historico"


def up(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS historico_atualizacoes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            data       TEXT NOT NULL,
            total_base INTEGER,
            novos      INTEGER,
            saidos     INTEGER,
            continuam  INTEGER,
            empresa    TEXT NOT NULL DEFAULT 'INEPROTEC'
        )
        """
    )


def down(conn):
    conn.execute("DROP TABLE IF EXISTS historico_atualizacoes")
