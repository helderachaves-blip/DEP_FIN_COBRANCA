#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para organizar as pastas do projeto MAT-INE Inadimplência
Cria a estrutura completa e move arquivos para os locais corretos
"""

import os
import shutil
from pathlib import Path

# Diretório raiz do projeto
PROJETO_DIR = Path(__file__).parent

print("=" * 70)
print("ORGANIZADOR DE PASTAS - MAT-INE INADIMPLÊNCIA 2026")
print("=" * 70)

# Estrutura de pastas a criar
PASTAS = [
    "00_DOCUMENTACAO",
    "01_SCRIPTS",
    "02_DADOS/BASE DE DADOS",
    "03_RELATORIOS",
    "04_LOGS",
    "05_GUIAS",
    "06_APP",
]

# Criar pastas
print("\n📁 Criando estrutura de pastas...")
for pasta in PASTAS:
    caminho = PROJETO_DIR / pasta
    caminho.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ {pasta}")

# Mapeamento de movimentação de arquivos
MOVIMENTOS = {
    # 00_DOCUMENTACAO
    "QUICK_START.txt": "00_DOCUMENTACAO/",
    "RESUMO_EXECUTIVO_PROJETO.md": "00_DOCUMENTACAO/",
    "RELATORIO_ANALISE_COMPLETA.md": "00_DOCUMENTACAO/",
    "ANALISE_PROCESSO_ATUAL_VS_NOVO.md": "00_DOCUMENTACAO/",
    "PLANO_DE_TRABALHO_DETALHADO.md": "00_DOCUMENTACAO/",
    "INDICE_COMPLETO.md": "00_DOCUMENTACAO/",
    "HANDOFF_PARA_PROXIMA_MAQUINA.md": "00_DOCUMENTACAO/",
    "PLANO_DE_ACOES.md": "00_DOCUMENTACAO/",
    "CRONOGRAMA_TAREFAS.csv": "00_DOCUMENTACAO/",
    "COMO_EXECUTAR_ANALISE.md": "00_DOCUMENTACAO/",

    # 01_SCRIPTS
    "inadimplencia_app.py": "01_SCRIPTS/",
    "consolidar_vencidas.py": "01_SCRIPTS/",
    "debug_cpf.py": "01_SCRIPTS/",
    "diagnostico.py": "01_SCRIPTS/",
    "ANALISE_DADOS.py": "01_SCRIPTS/",

    # 02_DADOS (já está lá, só confirmamos)

    # 05_GUIAS
    "GUIA_LUANA.txt": "05_GUIAS/",
    "CONSOLIDACAO_VENCIDAS_GUIA.md": "05_GUIAS/",
    "EXEMPLO_CONSOLIDACAO_VENCIDAS.md": "05_GUIAS/",
    "README_CONSOLIDACAO.txt": "05_GUIAS/",
}

# Executar movimentação
print("\n📦 Movendo arquivos...")
for arquivo_origem, pasta_destino in MOVIMENTOS.items():
    caminho_origem = PROJETO_DIR / arquivo_origem
    caminho_destino = PROJETO_DIR / pasta_destino / arquivo_origem

    if caminho_origem.exists():
        try:
            # Se arquivo já existe no destino, não faz nada
            if not caminho_destino.exists():
                shutil.move(str(caminho_origem), str(caminho_destino))
                print(f"  ✓ {arquivo_origem} → {pasta_destino}")
            else:
                print(f"  ⓘ {arquivo_origem} já existe em {pasta_destino}")
        except Exception as e:
            print(f"  ✗ ERRO ao mover {arquivo_origem}: {str(e)}")
    else:
        print(f"  ⓘ {arquivo_origem} não encontrado")

# Criar READMEs em cada pasta
print("\n📝 Criando README.md em cada pasta...")

README_TEMPLATES = {
    "00_DOCUMENTACAO": """# 📋 00_DOCUMENTACAO

**Pasta de Documentação do Projeto**

## 📁 Conteúdo

- QUICK_START.txt - Resumo em 1 página
- RESUMO_EXECUTIVO_PROJETO.md - Contexto completo
- RELATORIO_ANALISE_COMPLETA.md - Análise dos dados
- ANALISE_PROCESSO_ATUAL_VS_NOVO.md - Comparativo
- PLANO_DE_TRABALHO_DETALHADO.md - Arquitetura técnica
- PLANO_DE_ACOES.md - Plano com 4 fases
- INDICE_COMPLETO.md - Mapa visual do projeto

## 🎯 Como Usar

Se tem 5 min: Leia QUICK_START.txt
Se tem 15 min: Leia RESUMO_EXECUTIVO_PROJETO.md
Se quer tudo: Consulte INDICE_COMPLETO.md

---
**Data:** 20/05/2026
""",

    "01_SCRIPTS": """# 💻 01_SCRIPTS

**Scripts Python do Projeto**

## 📁 Arquivos

- **inadimplencia_app.py** - APLICAÇÃO PRINCIPAL (GUI)
- consolidar_vencidas.py - Script de consolidação (referência)
- debug_cpf.py - Debug de CPF
- diagnostico.py - Diagnóstico de CSV

## 🚀 Como Usar

Para rodar a aplicação principal:
```
python inadimplencia_app.py
```

## 📋 Dependências

- pandas
- openpyxl
- tkinter (incluso no Python)

Instalar: `pip install pandas openpyxl`

---
**Data:** 20/05/2026
""",

    "02_DADOS": """# 📊 02_DADOS

**Dados de Entrada do Projeto**

## 📁 Estrutura

```
02_DADOS/
└─ BASE DE DADOS/
   ├─ VENCIDOS - 19-05-2026.csv
   ├─ VENCIDOS - 19-05-2026.xlsx
   ├─ (298) Alunos.csv
   └─ NAO PAGOS - VINCENDAS - 19-05-2026.csv
```

## ℹ️ Informações

### Arquivo: VENCIDOS
- 297 faturas vencidas
- Valor: ~R$ 50.000+
- Separador: `;` (ponto e vírgula)
- Campos: Fatura #, Tipo, Aluno, CPF, Vencimento, Total, etc

### Arquivo: (298) Alunos
- 298 registros de alunos
- Campos: Nome, CPF, E-mail, Telefone, Ativo, Data de Cadastro
- Separador: `,` (vírgula)

## 🔄 Frequência de Atualização

- VENCIDOS: Diariamente (Luana baixa do Synapta)
- ALUNOS: Mensalmente (ou quando houver novo cadastro)

---
**Data:** 20/05/2026
""",

    "03_RELATORIOS": """# 📄 03_RELATORIOS

**Relatórios Gerados pela Aplicação**

## 📁 Conteúdo

Relatórios são gerados automaticamente pela `inadimplencia_app.py` e salvo aqui:

- `relatorio_categoria_A1_*.txt` - Categoria A1 (1 título, <365d)
- `relatorio_categoria_A1_*.xlsx` - Idem em Excel
- `relatorio_categoria_A2_*.txt` - Categoria A2 (1 título, >=365d)
- `relatorio_categoria_A2_*.xlsx` - Idem em Excel
- `relatorio_categoria_B_*.txt` - Categoria B (>1 título)
- `relatorio_categoria_B_*.xlsx` - Idem em Excel

## 📊 Informações

Cada relatório contém:
- Nome do aluno
- Telefone
- Valor total
- Dias de atraso
- Mensagem pronta para copiar no WhatsApp

---
**Data:** 20/05/2026
""",

    "04_LOGS": """# 📋 04_LOGS

**Logs de Execução da Aplicação**

## 📁 Conteúdo

- `app.log` - Log principal da aplicação

## ℹ️ Informações

O arquivo `app.log` registra:
- Inicializações da aplicação
- Consolidações de dados
- Gerações de relatórios
- Erros e avisos

## 🔍 Como Verificar

Abra `app.log` com um editor de texto simples para ver o histórico de execuções.

---
**Data:** 20/05/2026
""",

    "05_GUIAS": """# 📖 05_GUIAS

**Guias de Uso e Tutoriais**

## 📁 Conteúdo

- **GUIA_LUANA.txt** - Guia completo para Luana (operadora)
- CONSOLIDACAO_VENCIDAS_GUIA.md - Como consolidar vencidas
- EXEMPLO_CONSOLIDACAO_VENCIDAS.md - Exemplos de saída
- README_CONSOLIDACAO.txt - Quick start

## 🎯 Para Quem?

- **GUIA_LUANA.txt** → Para Luana usar a aplicação
- Outros → Para desenvolvimento/referência

---
**Data:** 20/05/2026
""",

    "06_APP": """# 🖥️ 06_APP

**Aplicação Desktop - Consolidador de Inadimplências**

## 📁 Conteúdo

- `inadimplencia_app.py` - Código principal (link para 01_SCRIPTS/)
- `requirements.txt` - Dependências Python
- `config.ini` - Configurações (criar se necessário)

## 🚀 Para Rodar

1. Instale dependências:
   ```
   pip install -r requirements.txt
   ```

2. Execute:
   ```
   python inadimplencia_app.py
   ```

## 📊 Fluxo

1. Baixa CSVs (VENCIDOS + ALUNOS) → BASE DE DADOS/
2. Clica "Consolidar Vencidas"
3. Clica "Gerar Relatório WhatsApp"
4. Relatórios salvos em 03_RELATORIOS/

---
**Data:** 20/05/2026
""",
}

for pasta, conteudo in README_TEMPLATES.items():
    arquivo = PROJETO_DIR / pasta / "README.md"
    if not arquivo.exists():
        arquivo.write_text(conteudo, encoding='utf-8')
        print(f"  ✓ {pasta}/README.md criado")
    else:
        print(f"  ⓘ {pasta}/README.md já existe")

# Criar requirements.txt
print("\n📦 Criando requirements.txt...")
requirements = """pandas==2.1.0
openpyxl==3.11.0
"""

req_file = PROJETO_DIR / "requirements.txt"
if not req_file.exists():
    req_file.write_text(requirements, encoding='utf-8')
    print("  ✓ requirements.txt criado")
else:
    print("  ⓘ requirements.txt já existe")

print("\n" + "=" * 70)
print("✅ ORGANIZAÇÃO COMPLETA!")
print("=" * 70)

print(f"\n📁 Estrutura criada em: {PROJETO_DIR}")
print("\nPróximos passos:")
print("  1. Revise a estrutura")
print("  2. Atualize MEMORY.md")
print("  3. Prepare para Claude Code")

print("\n" + "=" * 70)
