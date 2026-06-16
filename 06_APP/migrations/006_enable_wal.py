"""006 - WAL mode (DB-B01). PRAGMA journal_mode nao pode rodar dentro de transacao.

No-op em Postgres: WAL e o modo padrao e nao e configuravel por PRAGMA.
"""
import ddl

version = 6
name = "enable_wal"
transactional = False  # PRAGMA journal_mode=WAL deve rodar fora de transacao


def up(conn):
    if ddl.DIALECT == 'sqlite':
        conn.execute("PRAGMA journal_mode=WAL")


def down(conn):
    if ddl.DIALECT == 'sqlite':
        conn.execute("PRAGMA journal_mode=DELETE")
