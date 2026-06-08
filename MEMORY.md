# MEMORY - PROJETO INADIMPLÊNCIA MAT-INE 2026

**Última atualização:** 01/06/2026 — Sessão Claude Code
**Status:** ✅ FASE 1 EM USO | 🔧 AJUSTES EM ANDAMENTO | ⏳ CONVERSÃO WEB PLANEJADA
**Responsáveis:** Helder (TI) + Luana (Inadimplências)

---

## CONTEXTO DO PROJETO

### Objetivo
Automatizar cobrança de faturas vencidas — reduzir trabalho de 2.5-4h/dia para ~15 min/dia.
Comunicação via WhatsApp + gestão de tags no CRM Kommo.

### Empresas
- **INEPROTEC** — Escola Técnica
- **Matrícula EAD** — Consultoria Educacional (sistema: Synapta — portal.matriculaead.com.br)

### Operadoras
| Papel | Nome | Notas |
|-------|------|-------|
| TI/Arquitetura | Helder | helderachaves@gmail.com |
| Operadora diária | Luana | Não técnica — usa app via .bat |
| Gerente | Edilvo | gerente@ineprotec.com.br |

---

## STACK TÉCNICA

- **Python 3.14** — instalado em `C:\Users\Lorena\AppData\Local\Programs\Python\Python314\`
- **Dependências:** pandas 3.0.3, openpyxl 3.1.5, Pillow 12.2.0, tkinter (nativo)
- **pip** instalado via `ensurepip` (não estava presente inicialmente)
- **Launcher:** `ABRIR CONSOLIDADOR.bat` — detecta Python automaticamente pelo caminho completo

---

## ARQUITETURA ATUAL (FASE 1 — EM USO)

### Script principal
`01_SCRIPTS/inadimplencia_app.py` — ~870 linhas, GUI tkinter

### Constantes de path
```python
PROJETO_DIR        = Path(__file__).parent.parent
BASE_DE_DADOS_DIR  = PROJETO_DIR / "BASE DE DADOS"
RELATORIOS_DIR     = PROJETO_DIR / "RELATORIOS"
LOGS_DIR           = PROJETO_DIR / "LOGS"
BASE_INADIMPLENTES = BASE_DE_DADOS_DIR / "BASE_INADIMPLENTES.xlsx"
UTILITARIOS_DIR    = PROJETO_DIR / "UTILITARIOS"
```

### Fluxo operacional (Luana faz diariamente)
1. Baixa `(NNN) Faturas.csv` do Synapta (faturas vencidas)
2. Abre via `ABRIR CONSOLIDADOR.bat`
3. Carrega Alunos + Vencidos
4. Clica "Consolidar Vencidas" → tabela aparece (Cat A e Cat B)
5. Clica "Comparar e Atualizar Base" → gera relatórios
6. Clica "Gerar Relatório WhatsApp" → TXT com mensagens prontas
7. Copia/cola mensagens no WhatsApp Web manualmente

### Classificação de inadimplentes
```
Categoria A — 1 título em aberto com menos de 30 dias de atraso
  → Mensagem: aviso com boleto | Frequência: DIÁRIA

Categoria B — Todos os outros (>1 título OU >30 dias de atraso)
  → Mensagem: negociação/reativação | Frequência: 1x POR SEMANA
```

### Arquivos fonte (exportados do Synapta)
| Arquivo | Formato | Descrição |
|---------|---------|-----------|
| `(NNN) Faturas.csv` | CSV `,` sem título, utf-8 | Faturas vencidas |
| `(298) Alunos.csv` | CSV `,` | Cadastro de alunos (5.208 registros) |
| `NAO PAGOS - VINCENDAS - DD-MM-AAAA.csv` | CSV | Faturas a vencer (não usada na lógica) |

### Base persistente
`BASE DE DADOS/BASE_INADIMPLENTES.xlsx`
- Colunas: CPF, Aluno, Telefone, E-mail, Qtd_Boletos, Total, Ultimo_Vencimento, Dias_Atraso, Categoria, Data_Entrada
- `Data_Entrada` preservada para alunos que continuam inadimplentes

### Relatórios gerados (por data: RELATORIOS/2026/MM/DD/)
| Arquivo | Conteúdo |
|---------|---------|
| `relatorio_categoria_A_*.txt/.xlsx` | Mensagens WhatsApp Cat A |
| `relatorio_categoria_B_*.txt/.xlsx` | Mensagens WhatsApp Cat B |
| `NOVOS_INADIMPLENTES_*.txt/.xlsx` | Entrou na base → adicionar tag CRM |
| `QUITADOS_*.txt/.xlsx` | Saiu dos vencidos → revisar (pagou ou renegociou) |

---

## TEMPLATES DE MENSAGEM

### Mensagem A (Inadimplente Novo — Cat A)
```
Olá, {sr./sra.} {NOME}. Tudo bem?
Somos do setor financeiro do Matricula EaD.
Para sua maior comodidade estamos enviando o boleto referente ao seu Curso
Técnico, com vencimento em {DATA_VENCIMENTO}.
Se já realizou o pagamento, favor desconsiderar a mensagem!
Qualquer dúvida estamos à disposição!
```

### Mensagem B (Demais Inadimplentes — Cat B)
```
Olá, {sr./sra.} {NOME}. Tudo bem?
Somos do setor financeiro do Matricula EaD. O motivo do meu contato é
referente ás parcelas em aberto do seu Curso Técnico em Agropecuária.
Tem interesse em retornar ao curso?
```
**⚠️ Pendência:** "Curso Técnico em Agropecuária" está hardcoded — ver ajuste #3 abaixo.

**Detecção de gênero:** automática por heurística (nomes terminados em "a" → sra.)

---

## AJUSTES REALIZADOS NESTA SESSÃO (01/06/2026)

### Fix: ABRIR CONSOLIDADOR.bat
- **Problema:** Python não encontrado no PATH
- **Solução:** .bat detecta automaticamente `AppData\Local\Programs\Python\Python314\pythonw.exe`
- **Status:** ✅ Corrigido e funcionando

### Fix: Dependências Python
- **Problema:** pandas, openpyxl, Pillow não instalados
- **Solução:** `python -m ensurepip` + `pip install pandas openpyxl pillow`
- **Status:** ✅ Instalado (pandas 3.0.3, openpyxl 3.1.5, Pillow 12.2.0)

### Fix: Lógica de Renegociação no relatório QUITADOS
- **Problema:** Alunos que renegociam somem dos VENCIDOS → eram classificados como QUITADOS → dado errado no CRM
- **Tentativa:** Usar arquivo À Vencer para detectar renegociados — **não funcionou** (alunos quitados também aparecem no À Vencer por terem parcelas futuras do curso)
- **Solução atual:** Relatório "QUITADOS" renomeado para "SAÍRAM DOS VENCIDOS" com aviso de revisão manual e coluna `Situacao` em branco no XLSX para Luana marcar: Pagou ou Renegociou
- **Limitação reconhecida:** Separação automática quitado x renegociado requer banco de dados → aguarda versão web
- **Status:** ✅ Corrigido (revisão manual)

---

## ROADMAP DE AJUSTES PENDENTES

### Ajuste #1 — Renegociação (separação automática)
- **O que é:** Distinguir automaticamente quitados de renegociados sem intervenção manual
- **Por que não resolvemos:** Arquivo À Vencer contém todos os alunos com parcelas futuras, não só renegociados
- **Solução definitiva:** Banco de dados com campo `status` (QUITADO | RENEGOCIADO | INADIMPLENTE)
- **Quando:** Versão web

### Ajuste #2 — Templates de mensagem configuráveis
- **O que é:** Tela/aba para editar os templates A e B sem mexer no código
- **Por que:** Mensagem B tem curso hardcoded ("Agropecuária") — outros cursos ficam errados
- **Quando:** Próxima sessão (antes ou durante a web)

### Ajuste #3 — Dashboards e relatórios analíticos
- **O que é:**
  - Qtd inadimplentes quitados + valor por intervalo de datas
  - Qtd em renegociação + valor por intervalo de datas
- **Quando:** Versão web

### Ajuste #4 — Link de pagamento personalizado por aluno (ROADMAP)
- **O que é:** Inserir link PIX/boleto específico de cada aluno na mensagem de cobrança
- **Depende de:** API Synapta para buscar o link de cada fatura
- **Quando:** Fase 2 / versão web

---

## FASE 2 — PLANEJADA (versão web)

**Decisão tomada:** Converter para aplicação web para acomodar:
- Banco de dados (SQLite ou similar) para separar quitados x renegociados
- Editor de templates de mensagem via interface
- Dashboards analíticos com filtros por período
- Kommo CRM API — tagging automático (adicionar/remover tag INADIMPLENTE)
- API Synapta — buscar boletos sem exportar CSV manual
- WhatsApp automático via WAHA ou Twilio
- Agendamento diário/semanal

---

## PROBLEMAS CONHECIDOS E SOLUÇÕES

| # | Sintoma | Causa | Solução | Status |
|---|---------|-------|---------|--------|
| 1 | Separador CSV errado | Arquivo usa `;` não `,` | Loop testa múltiplos separadores | ✅ |
| 2 | Linha de título extra | Synapta exportava `(297) Faturas;;;` | skiprows=1 (formato mudou) | ✅ |
| 3 | Valores não convertiam | Formato brasileiro `R$ 1.024,62` | função converter_valor() | ✅ |
| 4 | 252 alunos sem telefone | CPF perdia zeros à esquerda | .str.zfill(11) | ✅ |
| 5 | Path quebrado | .parent apontava para 01_SCRIPTS/ | .parent.parent | ✅ |
| 6 | Gênero errado (sr. Vanessa) | Template fixo | detectar_tratamento() com heurística | ✅ |
| 7 | Novo export Synapta não lê | Formato mudou | Loop testa skip=[0,1] e sep=[`,`,`;`] | ✅ |
| 8 | Python não encontrado | PATH não configurado | .bat com caminho completo hardcoded | ✅ |
| 9 | Renegociados como quitados | Sem distinção automática | Revisão manual com planilha | ✅ (parcial) |

---

## CONTROLE DE VERSÃO

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.0–1.6 | 20/05 | App GUI base, correções diversas |
| 2.0 | 20/05 (noite) | Upload, data folder, base, logos, fix formato Synapta |
| 2.1 | 01/06/2026 | Fix .bat Python path, instalação dependências, fix lógica renegociação |

---

*Última atualização: 01/06/2026 — Sessão Claude Code — by Helder + Claude*
