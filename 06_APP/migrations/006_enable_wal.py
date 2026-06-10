"""006 - WAL mode (DB-B01). PRAGMA journal_mode nao pode rodar dentro de transacao."""

version = 6
name = "enable_wal"
transactional = False  # PRAGMA journal_mode=WAL deve rodar fora de transacao


def up(conn):
    conn.execute("PRAGMA journal_mode=WAL")


def down(conn):
    conn.execute("PRAGMA journal_mode=DELETE")
