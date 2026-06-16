"""Helpers de DDL cross-dialect (SQLite ↔ Postgres) para as migrations.

Lido de DATABASE_URL (mesma variável de database.py) para evitar import circular.
Importado por runner.py e por cada migration via sys.path (adicionado pelo runner).
"""
import os

DIALECT = 'postgres' if os.environ.get('DATABASE_URL') else 'sqlite'


def pk_int() -> str:
    """Coluna inteira auto-increment como PK."""
    if DIALECT == 'postgres':
        return 'INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY'
    return 'INTEGER PRIMARY KEY AUTOINCREMENT'


def blob() -> str:
    """Tipo de dado binário."""
    return 'BYTEA' if DIALECT == 'postgres' else 'BLOB'


def ts_default() -> str:
    """Cláusula DEFAULT de timestamp para colunas TEXT."""
    if DIALECT == 'postgres':
        return "DEFAULT to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS')"
    return "DEFAULT (datetime('now'))"
