# 📁 ESTRUTURA DE PASTAS - PROJETO INADIMPLÊNCIA

**Data:** 20/05/2026  
**Status:** Reorganização para Claude Code  
**Responsável:** Helder (TI)

---

## 🎯 ESTRUTURA FINAL

```
C:\Users\User\Desktop\MAT-INE - INADIMPLENCIA - 2026\
│
├─ README.md ................................. Índice principal (CRIAR)
├─ MEMORY.md .................................. Documentação de memória
│
├─ 📁 00_DOCUMENTACAO/
│  ├─ QUICK_START.txt ......................... Resumo rápido
│  ├─ RESUMO_EXECUTIVO_PROJETO.md ............ Contexto completo
│  ├─ HANDOFF_PARA_PROXIMA_MAQUINA.md ....... Transição
│  ├─ RELATORIO_ANALISE_COMPLETA.md ......... Análise dos dados
│  ├─ ANALISE_PROCESSO_ATUAL_VS_NOVO.md .... Comparativo
│  ├─ PLANO_DE_TRABALHO_DETALHADO.md ....... Arquitetura técnica
│  ├─ INDICE_COMPLETO.md ..................... Mapa do projeto
│  └─ PLANO_DE_ACOES.md ..................... Plano com 4 fases
│
├─ 📁 01_SCRIPTS/
│  ├─ inadimplencia_app.py ................... APP PRINCIPAL (GUI)
│  ├─ consolidar_vencidas.py ................ Script de consolidação (referência)
│  ├─ debug_cpf.py ........................... Script de diagnóstico
│  ├─ diagnostico.py ......................... Script de diagnóstico CSV
│  └─ README.md ............................. O que tem nesta pasta
│
├─ 📁 02_DADOS/
│  ├─ BASE DE DADOS/
│  │  ├─ VENCIDOS - 19-05-2026.csv ......... Entrada (faturas vencidas)
│  │  ├─ VENCIDOS - 19-05-2026.xlsx ....... Arquivo original
│  │  ├─ (298) Alunos.csv .................. Entrada (dados alunos)
│  │  ├─ NAO PAGOS - VINCENDAS - 19-05-2026.csv .... Futuro
│  │  └─ NAO PAGOS - VINCENDAS - 19-05-2026.xlsx
│  │
│  └─ README.md ............................. Instruções de dados
│
├─ 📁 03_RELATORIOS/
│  ├─ relatorio_categoria_A1_*.txt ......... Relatórios A1
│  ├─ relatorio_categoria_A1_*.xlsx ....... Relatórios A1 (Excel)
│  ├─ relatorio_categoria_A2_*.txt ......... Relatórios A2
│  ├─ relatorio_categoria_A2_*.xlsx ....... Relatórios A2 (Excel)
│  ├─ relatorio_categoria_B_*.txt ......... Relatórios B
│  ├─ relatorio_categoria_B_*.xlsx ........ Relatórios B (Excel)
│  └─ README.md ............................. Instruções de relatórios
│
├─ 📁 04_LOGS/
│  ├─ app.log ................................ Log da aplicação
│  └─ README.md ............................. Informações de logs
│
├─ 📁 05_GUIAS/
│  ├─ GUIA_LUANA.txt ......................... Guia de uso para Luana
│  ├─ CONSOLIDACAO_VENCIDAS_GUIA.md ........ Guia de consolidação
│  ├─ EXEMPLO_CONSOLIDACAO_VENCIDAS.md .... Exemplos de saída
│  ├─ README_CONSOLIDACAO.txt ............... Quick start consolidação
│  └─ README.md ............................. Índice de guias
│
└─ 📁 06_APP/
   ├─ inadimplencia_app.py .................. (CÓPIA - link simbólico para 01_SCRIPTS/)
   ├─ requirements.txt ....................... Dependências Python
   ├─ config.ini ............................. Configurações (criar se necessário)
   └─ README.md ............................. Documentação da app

```

---

## 📝 PRÓXIMAS AÇÕES

### Imediato:
- [ ] Criar estrutura de pastas
- [ ] Mover arquivos para locais corretos
- [ ] Criar README.md em cada pasta
- [ ] Atualizar MEMORY.md com nova estrutura

### Antes do Claude Code:
- [ ] Criar requirements.txt
- [ ] Documentar como rodar a app
- [ ] Criar .gitignore (se for usar Git)
- [ ] Checklist de validação

---

## 🔄 MAPEAMENTO DE MOVIMENTAÇÃO

| Arquivo Atual | Novo Local | Ação |
|---------------|-----------|------|
| QUICK_START.txt | 00_DOCUMENTACAO/ | Mover |
| RESUMO_EXECUTIVO_PROJETO.md | 00_DOCUMENTACAO/ | Mover |
| inadimplencia_app.py | 01_SCRIPTS/ | Mover |
| consolidar_vencidas.py | 01_SCRIPTS/ | Mover |
| debug_cpf.py | 01_SCRIPTS/ | Mover |
| diagnostico.py | 01_SCRIPTS/ | Mover |
| GUIA_LUANA.txt | 05_GUIAS/ | Mover |
| CONSOLIDACAO_VENCIDAS_GUIA.md | 05_GUIAS/ | Mover |
| RELATORIOS/* | 03_RELATORIOS/ | Mover quando gerados |
| LOGS/* | 04_LOGS/ | Mover quando gerados |

---

## ✅ BENEFÍCIOS DA NOVA ESTRUTURA

- ✅ Fácil de navegar
- ✅ Documentação centralizada
- ✅ Scripts organizados por função
- ✅ Dados separados de código
- ✅ Pronto para versionamento (Git)
- ✅ Escalável para Fase 2 (Kommo, etc)

---

**Status:** Pronto para reorganização  
**Data:** 20/05/2026 13:15
