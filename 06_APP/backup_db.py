"""Backup do banco SQLite com retenção.

Uso:
    python backup_db.py            # mantém os 14 backups mais recentes
    python backup_db.py --keep 30  # mantém os 30 mais recentes

Os backups vão para  {DATA_DIR}/backups/  (respeita MATINE_DATA_DIR; em produção
é C:\\MATINE\\backups). Usa a API `sqlite3.Connection.backup`, que faz uma cópia
consistente mesmo com o banco em WAL e em uso. Pode ser agendado no Agendador de
Tarefas do Windows para rodar diariamente.
"""
import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

import database as db  # DATA_DIR/DB_PATH (respeita MATINE_DATA_DIR)

BACKUP_DIR = db.DATA_DIR / 'backups'
PREFIXO = 'inadimplencia_backup_'


def _aplicar_retencao(keep: int) -> list[Path]:
    """Mantém só os `keep` backups mais recentes; remove o resto. Retorna os removidos."""
    if keep <= 0:
        return []
    backups = sorted(BACKUP_DIR.glob(f'{PREFIXO}*.db'),
                     key=lambda p: p.stat().st_mtime, reverse=True)
    removidos = []
    for antigo in backups[keep:]:
        antigo.unlink()
        removidos.append(antigo)
    return removidos


def fazer_backup(keep: int = 14) -> Path | None:
    """Cria um backup datado do banco e aplica a retenção.

    Retorna o caminho do backup criado, ou None se o banco ainda não existe.
    """
    if not db.DB_PATH.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    destino = BACKUP_DIR / f'{PREFIXO}{ts}.db'

    origem = sqlite3.connect(str(db.DB_PATH))
    try:
        dest = sqlite3.connect(str(destino))
        try:
            origem.backup(dest)   # cópia consistente (lida com WAL)
        finally:
            dest.close()
    finally:
        origem.close()

    _aplicar_retencao(keep)
    return destino


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Backup do banco MAT-INE com retenção.')
    ap.add_argument('--keep', type=int, default=14,
                    help='Quantos backups manter (default: 14).')
    args = ap.parse_args()

    bkp = fazer_backup(args.keep)
    if bkp:
        total = len(list(BACKUP_DIR.glob(f'{PREFIXO}*.db')))
        print(f'Backup criado: {bkp}')
        print(f'Backups mantidos: {total} (retenção: {args.keep})')
    else:
        print(f'Banco não encontrado em {db.DB_PATH} — nada a fazer.')
