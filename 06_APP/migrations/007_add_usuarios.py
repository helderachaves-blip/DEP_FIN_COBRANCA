"""007 - Tabela de usuarios (autenticacao multi-usuario via banco)."""

version = 7
name = "add_usuarios"


def up(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario    TEXT NOT NULL UNIQUE,
            nome       TEXT DEFAULT '',
            senha_hash TEXT NOT NULL,
            is_admin   INTEGER NOT NULL DEFAULT 0,
            ativo      INTEGER NOT NULL DEFAULT 1,
            criado_em  TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_usuario ON usuarios(usuario)")


def down(conn):
    conn.execute("DROP INDEX IF EXISTS idx_usuarios_usuario")
    conn.execute("DROP TABLE IF EXISTS usuarios")
