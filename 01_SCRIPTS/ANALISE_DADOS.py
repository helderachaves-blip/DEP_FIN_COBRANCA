#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar os arquivos de faturas
Salva um relatório em ANALISE_RESULTADO.txt
"""

import pandas as pd
import os

# Caminhos dos arquivos
pasta_base = r"C:\Users\User\Desktop\MAT-INE - INADIMPLENCIA - 2026\BASE DE DADOS"
arquivo_vencidos = os.path.join(pasta_base, "VENCIDOS - 19-05-2026.xlsx")
arquivo_vincendas = os.path.join(pasta_base, "NAO PAGOS - VINCENDAS - 19-05-2026.xlsx")

# Arquivo de saída
arquivo_saida = os.path.join(os.path.dirname(pasta_base), "ANALISE_RESULTADO.txt")

# Abrir arquivo para escrita
with open(arquivo_saida, 'w', encoding='utf-8') as f:

    # ARQUIVO 1: VENCIDOS
    f.write("="*100 + "\n")
    f.write("📊 ARQUIVO 1: VENCIDOS - 19-05-2026.xlsx\n")
    f.write("="*100 + "\n\n")

    try:
        vencidos = pd.read_excel(arquivo_vencidos)

        f.write(f"✓ Total de registros: {len(vencidos)}\n")
        f.write(f"✓ Total de colunas: {len(vencidos.columns)}\n")
        f.write(f"✓ Nomes das colunas: {list(vencidos.columns)}\n\n")

        f.write("📋 Primeiras 15 linhas:\n")
        f.write(vencidos.head(15).to_string())
        f.write("\n\n")

        f.write("📊 Tipos de dados:\n")
        f.write(str(vencidos.dtypes))
        f.write("\n\n")

        f.write("📈 Resumo estatístico:\n")
        f.write(str(vencidos.describe()))
        f.write("\n\n")

        f.write("📌 Dados únicos por coluna:\n")
        for col in vencidos.columns:
            f.write(f"  {col}: {vencidos[col].nunique()} valores únicos\n")
        f.write("\n")

    except Exception as e:
        f.write(f"❌ Erro ao ler: {e}\n\n")

    # ARQUIVO 2: VINCENDAS
    f.write("="*100 + "\n")
    f.write("📊 ARQUIVO 2: NÃO PAGOS - VINCENDAS - 19-05-2026.xlsx\n")
    f.write("="*100 + "\n\n")

    try:
        vincendas = pd.read_excel(arquivo_vincendas)

        f.write(f"✓ Total de registros: {len(vincendas)}\n")
        f.write(f"✓ Total de colunas: {len(vincendas.columns)}\n")
        f.write(f"✓ Nomes das colunas: {list(vincendas.columns)}\n\n")

        f.write("📋 Primeiras 15 linhas:\n")
        f.write(vincendas.head(15).to_string())
        f.write("\n\n")

        f.write("📊 Tipos de dados:\n")
        f.write(str(vincendas.dtypes))
        f.write("\n\n")

        f.write("📈 Resumo estatístico:\n")
        f.write(str(vincendas.describe()))
        f.write("\n\n")

        f.write("📌 Dados únicos por coluna:\n")
        for col in vincendas.columns:
            f.write(f"  {col}: {vincendas[col].nunique()} valores únicos\n")
        f.write("\n")

    except Exception as e:
        f.write(f"❌ Erro ao ler: {e}\n\n")

print(f"✓ Análise concluída! Arquivo salvo em: {arquivo_saida}")
print("  Abra o arquivo para ver os detalhes dos dados.")
