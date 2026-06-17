"""
Runner de migrations dual-dialect (STORY-01-05 / EPIC-02 Onda 1–2).

Cada migration e um arquivo `NNN_nome.py` neste diretorio, com:
    version       : int            - numero da migration (unico, crescente)
    name          : str            - nome curto
    up(conn)      : aplica         - usar conn.execute() por statement (NAO executescript)
    down(conn)    : reverte
    transactional : bool opcional  - default True; False para PRAGMAs (ex.: WAL)

Regras importantes:
- A conexao passada DEVE estar em autocommit (`conn.isolation_level = None`) para que o
  controle manual de transacao (BEGIN/COMMIT) funcione.
- `up()`/`down()` NUNCA devem usar `executescript` (ele forca um COMMIT implicito e quebra
  a atomicidade da transacao da migration). Use um `conn.execute()` por statement.
- Cada migration e aplicada de forma atomica: BEGIN -> up() -> registra versao -> COMMIT.
  Em erro, ROLLBACK. Migrations com `transactional = False` rodam fora de transacao
  (necessario para `PRAGMA journal_mode=WAL`).
"""

import importlib.util
import sys
from pathlib import Path

# Garante que migrations/ esteja no sys.path para que os arquivos de migration
# possam fazer `import ddl` sem caminhos absolutos.
_MIGRATIONS_DIR = str(Path(__file__).parent)
if _MIGRATIONS_DIR not in sys.path:
    sys.path.insert(0, _MIGRATIONS_DIR)

import ddl  # noqa: E402 — precisa vir após o sys.path acima


# Advisory lock para serializar a aplicação de migrations entre processos concorrentes.
# No deploy (gunicorn -w N) cada worker importa o app e chama init_db no boot; sem o lock,
# dois workers podem ver a mesma migration como pendente e o perdedor falha com chave
# duplicada em schema_migrations (PK), derrubando o worker. No Postgres usamos um advisory
# lock de SESSÃO (retido entre transações até unlock ou fechamento da conexão); no SQLite,
# onde só há um processo local, é no-op.
_MIGRATION_LOCK_KEY = 728913  # constante arbitrária e fixa (chave do advisory lock)


def acquire_lock(conn) -> None:
    """Adquire o advisory lock de migrations. Bloqueia até obter (Postgres); no-op em SQLite."""
    if ddl.DIALECT == 'postgres':
        conn.execute(f"SELECT pg_advisory_lock({_MIGRATION_LOCK_KEY})")


def release_lock(conn) -> None:
    """Libera o advisory lock de migrations. No-op em SQLite."""
    if ddl.DIALECT == 'postgres':
        conn.execute(f"SELECT pg_advisory_unlock({_MIGRATION_LOCK_KEY})")


def ensure_migrations_table(conn) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        " version INTEGER PRIMARY KEY,"
        " name TEXT NOT NULL,"
        f" applied_at TEXT NOT NULL {ddl.ts_default()}"
        ")"
    )


def applied_versions(conn) -> set:
    rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    return {r['version'] for r in rows}


def current_version(conn) -> int:
    row = conn.execute("SELECT MAX(version) AS max_ver FROM schema_migrations").fetchone()
    return (row['max_ver'] or 0) if row else 0


def discover(migrations_dir: Path) -> list:
    """Carrega os modulos de migration por caminho (nomes comecam com digito)."""
    mods = []
    for f in sorted(Path(migrations_dir).glob("*.py")):
        if not f.stem[0].isdigit():
            continue
        spec = importlib.util.spec_from_file_location(f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mods.append(mod)
    mods.sort(key=lambda m: m.version)
    return mods


def apply_pending(conn, migrations_dir: Path, log=lambda *_: None) -> list:
    """Aplica em ordem as migrations cuja versao ainda nao foi registrada. Retorna as versoes aplicadas.

    Protegido por advisory lock (acquire_lock): serializa workers concorrentes no Postgres
    para que dois processos nao apliquem a mesma migration em paralelo. O lock e liberado
    no finally (e, como fallback, ao fechar a conexao).
    """
    acquire_lock(conn)
    try:
        ensure_migrations_table(conn)
        applied = applied_versions(conn)
        done = []
        for m in discover(migrations_dir):
            if m.version in applied:
                continue
            transactional = getattr(m, "transactional", True)
            if transactional:
                conn.execute("BEGIN")
                try:
                    m.up(conn)
                    conn.execute(
                        "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                        (m.version, m.name),
                    )
                    conn.execute("COMMIT")
                except Exception:
                    conn.execute("ROLLBACK")
                    raise
            else:
                m.up(conn)
                conn.execute(
                    "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                    (m.version, m.name),
                )
            log(f"  migration {m.version:03d} ({m.name}) aplicada")
            done.append(m.version)
        return done
    finally:
        release_lock(conn)
