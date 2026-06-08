import pandas as pd
from pathlib import Path

BASE_DE_DADOS_DIR = Path(r"C:\Users\User\Desktop\MAT-INE - INADIMPLENCIA - 2026\BASE DE DADOS")
VENCIDOS_PATH = BASE_DE_DADOS_DIR / "VENCIDOS - 19-05-2026.csv"
ALUNOS_PATH = BASE_DE_DADOS_DIR / "(298) Alunos.csv"

print("=" * 70)
print("DEBUG: Verificando CPF")
print("=" * 70)

# Ler VENCIDOS
vencidos = pd.read_csv(str(VENCIDOS_PATH), encoding='latin1', sep=';', skiprows=1)
print(f"\nVENCIDOS - Colunas: {list(vencidos.columns)}")
print(f"Primeiros CPFs do VENCIDOS:")
print(vencidos[['Aluno', 'CPF sem mask']].head(10))

# Ler ALUNOS
alunos = pd.read_csv(str(ALUNOS_PATH), encoding='latin1')
print(f"\n\nALUNOS - Colunas: {list(alunos.columns)}")
print(f"Primeiros CPFs do ALUNOS:")
print(alunos[['Nome', 'CPF']].head(10))

# Tentar match
print("\n\n" + "=" * 70)
print("Tentando match de CPF:")
print("=" * 70)

# Preparar CPFs
vencidos_cpf = vencidos['CPF sem mask'].astype(str).str.strip().unique()
print(f"\nTotal de CPFs únicos em VENCIDOS: {len(vencidos_cpf)}")
print(f"Exemplo de CPF VENCIDOS: {vencidos_cpf[0]}")

alunos['CPF_sem_mask'] = alunos['CPF'].str.replace('.', '').str.replace('-', '')
alunos_cpf = alunos['CPF_sem_mask'].astype(str).str.strip().unique()
print(f"\nTotal de CPFs únicos em ALUNOS: {len(alunos_cpf)}")
print(f"Exemplo de CPF ALUNOS: {alunos_cpf[0]}")

# Contar matches
matches = vencidos['CPF sem mask'].astype(str).isin(alunos['CPF_sem_mask'].astype(str)).sum()
print(f"\nTotal de matches encontrados: {matches}/{len(vencidos)}")

# Achar CPFs que não matcham
vencidos_nao_match = vencidos[~vencidos['CPF sem mask'].astype(str).isin(alunos['CPF_sem_mask'].astype(str))]['CPF sem mask'].unique()
print(f"\nCPFs que NÃO encontram match: {len(vencidos_nao_match)}")
print(f"Exemplos de CPFs não encontrados:")
for cpf in vencidos_nao_match[:5]:
    print(f"  {cpf}")
