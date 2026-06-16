"""
Runner de migrations dual-dialect (STORY-01-05 / EPIC-02 Onda 1).

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
from pathlib import Path


def ensure_migrations_table(conn) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        " version INTEGER PRIMARY KEY,"
        " name TEXT NOT NULL,"
        " applied_at TEXT NOT NULL DEFAULT (datetime('now'))"
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
    """Aplica em ordem as migrations cuja versao ainda nao foi registrada. Retorna as versoes aplicadas."""
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
