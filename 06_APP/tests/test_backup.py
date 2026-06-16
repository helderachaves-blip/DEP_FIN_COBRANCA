"""Testes do backup_db.py — criação de backup válido e retenção."""
import sqlite3

import pytest

import backup_db


def _limpar_backups():
    backup_db.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for f in backup_db.BACKUP_DIR.glob(f'{backup_db.PREFIXO}*.db'):
        f.unlink()


@pytest.mark.sqlite_only
def test_backup_cria_arquivo_valido(db):
    """Gera um backup que é um SQLite válido com o schema versionado."""
    assert db.DB_PATH.exists()           # app/init já criou o banco no temp da sessão
    _limpar_backups()

    bkp = backup_db.fazer_backup(keep=14)
    assert bkp is not None and bkp.exists()

    conn = sqlite3.connect(str(bkp))
    try:
        versoes = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0]
        tem_usuarios = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='usuarios'"
        ).fetchone()
    finally:
        conn.close()
    assert versoes >= 7
    assert tem_usuarios is not None


def test_retencao_mantem_apenas_keep(db):
    """A retenção mantém exatamente os N backups mais recentes."""
    _limpar_backups()
    # cria 5 backups simulados com mtimes crescentes
    for i in range(5):
        p = backup_db.BACKUP_DIR / f'{backup_db.PREFIXO}2026010{i}_000000.db'
        p.write_text('x', encoding='utf-8')

    removidos = backup_db._aplicar_retencao(keep=2)
    restantes = list(backup_db.BACKUP_DIR.glob(f'{backup_db.PREFIXO}*.db'))
    assert len(restantes) == 2
    assert len(removidos) == 3


@pytest.mark.sqlite_only
def test_backup_sem_banco_retorna_none(db, monkeypatch, tmp_path):
    """Se o banco não existe, fazer_backup retorna None sem erro."""
    monkeypatch.setattr(backup_db.db, 'DB_PATH', tmp_path / 'inexistente.db')
    assert backup_db.fazer_backup() is None
