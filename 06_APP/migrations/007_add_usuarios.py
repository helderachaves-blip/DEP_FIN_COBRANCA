"""007 - Tabela de usuarios (autenticacao multi-usuario via banco)."""
import ddl

version = 7
name = "add_usuarios"


def up(conn):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS usuarios (
            id         {ddl.pk_int()},
            usuario    TEXT NOT NULL UNIQUE,
            nome       TEXT DEFAULT '',
            senha_hash TEXT NOT NULL,
            is_admin   INTEGER NOT NULL DEFAULT 0,
            ativo      INTEGER NOT NULL DEFAULT 1,
            criado_em  TEXT NOT NULL {ddl.ts_default()}
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_usuario ON usuarios(usuario)")


def down(conn):
    conn.execute("DROP INDEX IF EXISTS idx_usuarios_usuario")
    conn.execute("DROP TABLE IF EXISTS usuarios")
