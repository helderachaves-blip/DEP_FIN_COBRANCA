# HANDOFF — ESTADO ATUAL DO PROJETO
**Atualizado em:** 08/06/2026  
**Branch:** `homologacao`

---

## CONTEXTO RÁPIDO

- **Empresa:** Matricula EaD / Ineprotec (sistema multi-empresa)
- **Responsável:** EDILVO (gerente@ineprotec.com.br)
- **Objetivo:** Automatizar cobranças de inadimplência (2.5-4h/dia → 15 min/dia)
- **Aplicação:** Flask (Python) — web app local em `06_APP/`

---

## COMO RODAR A APLICAÇÃO

```powershell
# Iniciar
cd "F:\DADOS\CONSULTORIA\EDILVO SOUSA\AUTOMACOES IA\dep-financeiro\mat-ine - inadimplencia - 2026\06_APP"
python app.py
# Acesse: http://localhost:5000

# Parar (PowerShell)
Get-Process python* | Stop-Process -Force
```

---

## ESTADO DO DESENVOLVIMENTO

### Fases concluídas (código em 06_APP/)

| Fase | Descrição |
|------|-----------|
| A–C | Análise, consolidação e base de dados |
| D | Multi-empresa (Ineprotec + Matrícula EaD) |
| E | Arquivo "A Vencer" (boletos vincendos) |
| F | Aba Envio de Mensagens (marcar WhatsApp enviado) |
| G | Cobranças por E-mail via SMTP |

---

## PRÓXIMAS TAREFAS — APROVADAS E PRONTAS PARA IMPLEMENTAR

Plano completo em:
```
C:\Users\Lorena\.claude\plans\claude-vamos-organizar-um-tranquil-yeti.md
```

### Resumo das 5 mudanças aprovadas:

| # | O que fazer | Arquivo principal |
|---|-------------|-------------------|
| 1 | Aba Resultado: remover 4 botões (Gerar Relatórios, Envio de Mensagens, Atualizar Base, Relatórios) — mantém só Limpar | `templates/resultado.html` |
| 2 | Após clicar "Gerar Relatório" na Aba Início → redirecionar para `/resultado` (não mais para wizard) | `app.py` linha ~401 |
| 3 | Renomear `wizard_whatsapp` → `envio_mensagens` em todos os arquivos (função, rota, template) | `app.py`, `layout.html`, renomear `wizard_whatsapp.html` |
| 4 | Botão "Enviar WhatsApp" na Aba Envio de Mensagens → gera planilha XLSX para pasta sincronizada com Google Drive, com coluna Tag (tag vem do template cadastrado em Configurações) | `app.py`, `database.py`, `processing.py`, `configuracoes.html`, template renomeado |
| 5 | Aba Base: substituir dropdowns por 4 botões de filtro rápido (Novos Inadimplentes / Inadimplentes / Em Renegociação / Inadimplentes Quitados) com mini dashboard por filtro ativo | `templates/base.html` |

---

## FASE H — ROADMAP FUTURO (após as 5 mudanças acima)

**Configuração WhatsApp para clientes sem CRM:**
- Nova aba "WhatsApp" em Configurações
- Campos: Provedor (WAHA / Evolution API / Z-API / Twilio), URL, Token, Instância
- Botão Testar Conexão
- O botão "Enviar WhatsApp" na aba Envio de Mensagens terá comportamento adaptativo:
  - Com CRM → gera planilha (já implementado)
  - Com API WhatsApp → envia mensagens diretamente
  - Nenhum configurado → orienta o usuário

---

## ESTRUTURA DE ARQUIVOS IMPORTANTES

```
06_APP/
├── app.py              ← Rotas Flask, lógica de negócio
├── database.py         ← SQLite (C:\MATINE\banco\inadimplencia.db)
├── processing.py       ← Consolidação de dados, geração TXT/XLSX
├── templates/
│   ├── layout.html     ← Sidebar + topbar (Bootstrap 5.3.3)
│   ├── index.html      ← Aba Início
│   ├── resultado.html  ← Aba Resultado
│   ├── wizard_whatsapp.html  ← Aba Envio de Mensagens (SERÁ RENOMEADO)
│   ├── base.html       ← Aba Base de Inadimplentes
│   └── configuracoes.html   ← Aba Configurações
└── static/
    ├── logo-ineprotec.png
    └── logo-matriculaead.png

C:\MATINE\
├── uploads/{EMPRESA}/{vencidos|avencer|alunos}/
├── relatorios/{EMPRESA}/{ano}/{mes}/{dia}/
├── estado/estado_{empresa}.pkl
├── banco/inadimplencia.db
└── logs/app_web.log
```

---

## GIT PENDENTE (não commitado)

```
D  05_GUIAS/GUIA_LUANA.txt        (deletado)
?? 05_GUIAS/GUIA_BOAS_PRATICAS_GIT.md  (novo)
?? 05_GUIAS/GUIA_USUARIO.txt      (novo)
M  06_APP/templates/*.html        (modificados pelo usuário externamente)
```

---

## DADOS DO SISTEMA

- **600 faturas** analisadas (~R$ 95.000 em risco)
- ~200-250 clientes únicos
- Multi-empresa: INEPROTEC e MATRICULAEAD
- Dados sensíveis: CPF, nome, valor de dívida (manter pasta restrita)

---

**Próximo passo:** Implementar as Mudanças 1 a 5 conforme o plano aprovado.  
Referência: `C:\Users\Lorena\.claude\plans\claude-vamos-organizar-um-tranquil-yeti.md`
