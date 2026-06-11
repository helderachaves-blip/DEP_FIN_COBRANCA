"""Testes do runner de migrations e do schema versionado."""
import sqlite3


_TABELAS_ESPERADAS = {
    'schema_migrations', 'inadimplentes', 'templates', 'envios',
    'config_email', 'historico_atualizacoes', 'usuarios',
}


def _tabelas(conn) -> set:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return {r[0] for r in rows}


def test_schema_completo_apos_init(db):
    """init_db (rodou no import do app) deixou todas as tabelas e migrations 1-7."""
    with db.get_conn() as conn:
        tabelas = _tabelas(conn)
        versoes = {r[0] for r in conn.execute(
            "SELECT version FROM schema_migrations").fetchall()}
    assert _TABELAS_ESPERADAS.issubset(tabelas)
    assert {1, 2, 3, 4, 5, 6, 7}.issubset(versoes)


def test_runner_fresh_e_idempotente(tmp_path, db):
    """Em um banco novo, aplica 1-7 e a 2ª passada não aplica nada."""
    conn = sqlite3.connect(str(tmp_path / 'fresh.db'))
    conn.isolation_level = None  # runner controla as transações
    try:
        aplicadas = db.runner.apply_pending(conn, db.MIGRATIONS_DIR)
        assert aplicadas == [1, 2, 3, 4, 5, 6, 7]
        assert 'usuarios' in _tabelas(conn)

        de_novo = db.runner.apply_pending(conn, db.MIGRATIONS_DIR)
        assert de_novo == []
    finally:
        conn.close()


def test_migration_007_up_down(tmp_path, db):
    """A migration 007 cria e remove a tabela usuarios (up/down)."""
    mods = {m.version: m for m in db.runner.discover(db.MIGRATIONS_DIR)}
    m007 = mods[7]
    assert m007.name == 'add_usuarios'

    conn = sqlite3.connect(str(tmp_path / 'm007.db'))
    try:
        m007.up(conn)
        assert 'usuarios' in _tabelas(conn)
        # colunas essenciais
        cols = {r[1] for r in conn.execute("PRAGMA table_info(usuarios)").fetchall()}
        assert {'usuario', 'senha_hash', 'is_admin', 'ativo'}.issubset(cols)

        m007.down(conn)
        assert 'usuarios' not in _tabelas(conn)
    finally:
        conn.close()
