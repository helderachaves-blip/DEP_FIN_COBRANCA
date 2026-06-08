import pandas as pd
from pathlib import Path

BASE_DE_DADOS_DIR = Path(r"C:\Users\User\Desktop\MAT-INE - INADIMPLENCIA - 2026\BASE DE DADOS")
VENCIDOS_PATH = BASE_DE_DADOS_DIR / "VENCIDOS - 19-05-2026.csv"
ALUNOS_PATH = BASE_DE_DADOS_DIR / "(298) Alunos.csv"

print("=" * 70)
print("DIAGNOSTICO DE ARQUIVOS CSV")
print("=" * 70)

print("\nVerificando VENCIDOS - 19-05-2026.csv")
print(f"Caminho: {VENCIDOS_PATH}")
print(f"Existe: {VENCIDOS_PATH.exists()}")

if VENCIDOS_PATH.exists():
    for sep in [';', ',', '\t']:
        try:
            df = pd.read_csv(str(VENCIDOS_PATH), encoding='utf-8', sep=sep, nrows=1)
            print(f"\nSeparador: '{sep}'")
            print(f"Colunas: {list(df.columns)}")
            break
        except:
            try:
                df = pd.read_csv(str(VENCIDOS_PATH), encoding='latin1', sep=sep, nrows=1)
                print(f"\nSeparador (latin1): '{sep}'")
                print(f"Colunas: {list(df.columns)}")
                break
            except:
                pass

print("\n\nVerificando (298) Alunos.csv")
print(f"Caminho: {ALUNOS_PATH}")
print(f"Existe: {ALUNOS_PATH.exists()}")

if ALUNOS_PATH.exists():
    for sep in [',', ';', '\t']:
        try:
            df = pd.read_csv(str(ALUNOS_PATH), encoding='utf-8', sep=sep, nrows=1)
            print(f"\nSeparador: '{sep}'")
            print(f"Colunas: {list(df.columns)}")
            break
        except:
            try:
                df = pd.read_csv(str(ALUNOS_PATH), encoding='latin1', sep=sep, nrows=1)
                print(f"\nSeparador (latin1): '{sep}'")
                print(f"Colunas: {list(df.columns)}")
                break
            except:
                pass

print("\n" + "=" * 70)
