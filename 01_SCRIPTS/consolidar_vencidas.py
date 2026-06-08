#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para consolidar faturas vencidas por aluno
Junta dados de VENCIDOS com informações de contato de ALUNOS
"""

import pandas as pd
from datetime import datetime

# Paths dos arquivos
vencidos_path = r"C:\Users\User\Desktop\MAT-INE - INADIMPLENCIA - 2026\BASE DE DADOS\VENCIDOS - 19-05-2026.csv"
alunos_path = r"C:\Users\User\Desktop\INADIMPLÊNCIA MATRICULA EAD - 2026\00 - BASE DE DADOS\(298) Alunos.csv"
output_path = r"C:\Users\User\Desktop\MAT-INE - INADIMPLENCIA - 2026\CONSOLIDACAO_VENCIDAS_POR_ALUNO.xlsx"

print("=" * 80)
print("CONSOLIDAÇÃO DE FATURAS VENCIDAS POR ALUNO")
print("=" * 80)

# 1. Carregar arquivos
print("\n📂 Lendo arquivo VENCIDOS...")
try:
    vencidos = pd.read_csv(vencidos_path, encoding='utf-8', sep=';')
except:
    vencidos = pd.read_csv(vencidos_path, encoding='latin1', sep=';')

print(f"✓ {len(vencidos)} registros carregados")

print("\n📂 Lendo arquivo ALUNOS...")
try:
    alunos = pd.read_csv(alunos_path, encoding='utf-8')
except:
    alunos = pd.read_csv(alunos_path, encoding='latin1')

print(f"✓ {len(alunos)} registros carregados")

# 2. Limpar e preparar dados de VENCIDOS
print("\n🔧 Preparando dados...")

# Remover espaços extras
vencidos['Aluno'] = vencidos['Aluno'].str.strip()
vencidos['CPF sem mask'] = vencidos['CPF sem mask'].astype(str).str.strip()

# Converter datas
vencidos['Vencimento'] = pd.to_datetime(vencidos['Vencimento'], format='%d/%m/%Y')

# 3. Consolidar por aluno
print("🔄 Consolidando por aluno...")
consolidacao = vencidos.groupby('CPF sem mask').agg({
    'Aluno': 'first',  # Nome do aluno
    'Fatura #': 'count',  # Quantidade de boletos
    'Vencimento': 'max',  # Último vencimento (mais recente)
    'Total': 'sum'  # Total consolidado
}).reset_index()

# Renomear colunas
consolidacao.columns = ['CPF', 'Aluno', 'Qty_Boletos', 'Ultimo_Vencimento', 'Total_Consolidado']

# 4. Limpar CPF para merge
print("🔗 Joinando com dados de contato...")
consolidacao['CPF_mask'] = consolidacao['CPF'].astype(str)
alunos['CPF_sem_mask'] = alunos['CPF'].str.replace('.', '').str.replace('-', '')

# Fazer join com alunos para pegar email e telefone
consolidacao_final = consolidacao.merge(
    alunos[['CPF_sem_mask', 'E-mail', 'Telefone']],
    left_on='CPF',
    right_on='CPF_sem_mask',
    how='left'
)

# 5. Formatar resultado
print("📊 Formatando resultado...")

# Reordenar e renomear colunas finais
consolidacao_final = consolidacao_final[[
    'Aluno',
    'Qty_Boletos',
    'Ultimo_Vencimento',
    'Total_Consolidado',
    'Telefone',
    'E-mail',
    'CPF_mask'
]].rename(columns={
    'Aluno': 'Nome Aluno',
    'Qty_Boletos': 'Qtd Boletos',
    'Ultimo_Vencimento': 'Último Vencimento',
    'Total_Consolidado': 'Total (R$)',
    'Telefone': 'Telefone',
    'E-mail': 'E-mail',
    'CPF_mask': 'CPF'
})

# Formatar data
consolidacao_final['Último Vencimento'] = consolidacao_final['Último Vencimento'].dt.strftime('%d/%m/%Y')

# Ordenar por Último Vencimento (mais antigos primeiro)
consolidacao_final = consolidacao_final.sort_values('Último Vencimento')

# 6. Salvar em Excel
print(f"💾 Salvando resultado em: {output_path}")
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    consolidacao_final.to_excel(writer, index=False, sheet_name='Consolidação')

    # Adicionar formatação
    worksheet = writer.sheets['Consolidação']

    # Auto-adjust column widths
    for column in worksheet.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

# 7. Exibir resumo
print("\n" + "=" * 80)
print("✅ CONSOLIDAÇÃO CONCLUÍDA")
print("=" * 80)
print(f"\n📊 RESUMO:")
print(f"  • Total de alunos com boletos vencidos: {len(consolidacao_final)}")
print(f"  • Total de boletos: {consolidacao_final['Qtd Boletos'].sum():.0f}")
print(f"  • Valor total em atraso: R$ {consolidacao_final['Total (R$)'].sum():,.2f}")
print(f"  • Valor médio por aluno: R$ {consolidacao_final['Total (R$)'].mean():,.2f}")
print(f"  • Maior inadimplência: R$ {consolidacao_final['Total (R$)'].max():,.2f}")
print(f"\n  ✓ Alunos com email encontrado: {consolidacao_final['E-mail'].notna().sum()}")
print(f"  ✓ Alunos com telefone encontrado: {consolidacao_final['Telefone'].notna().sum()}")

print(f"\n📁 Arquivo salvo em:")
print(f"   {output_path}")

# 8. Mostrar top 10 maiores inadimplências
print("\n" + "=" * 80)
print("🔴 TOP 10 MAIORES INADIMPLÊNCIAS")
print("=" * 80)
top10 = consolidacao_final.nlargest(10, 'Total (R$)')[['Nome Aluno', 'Qtd Boletos', 'Total (R$)', 'Telefone', 'E-mail']]
for idx, (i, row) in enumerate(top10.iterrows(), 1):
    print(f"\n{idx}. {row['Nome Aluno']}")
    print(f"   Boletos: {row['Qtd Boletos']:.0f}  |  Total: R$ {row['Total (R$)']:,.2f}")
    print(f"   Tel: {row['Telefone'] if pd.notna(row['Telefone']) else 'N/A'}")
    print(f"   Email: {row['E-mail'] if pd.notna(row['E-mail']) else 'N/A'}")

print("\n" + "=" * 80)
