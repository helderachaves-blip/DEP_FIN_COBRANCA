# PLANO DE AÇÃO — MAT-INE Inadimplência 2026

> Sprint atual e próximos passos. Atualizar a cada sessão.
> Quando um item é entregue: marca ✅ aqui e registra no ROADMAP.md.
> Última atualização: 11/06/2026

---

## Estado Atual

- **Branch:** `homologacao`
- **Fase do produto:** Fases A–G + EPIC-01 (Sprint Zero) **100% concluídos**. Fase H em andamento — brainstorm realizado em 11/06/2026, STORY-H-01 pronta para implementação.
- **Último commit no remoto:** `524da68` — docs: brainstorm Fase H (WhatsApp/GDrive/Kommo + visão SaaS multi-tenant)
- **Pendente de push:** nada — `origin/homologacao` sincronizado *(aguardando PAT do GitHub para confirmar)*
- **App:** roda com `python app.py` em `06_APP/` → http://localhost:5000. Estrutura `C:\MATINE` criada automaticamente no startup.

---

## O Que Está Pendente

### Pendente de implementação
- **STORY-H-01** — Integração WhatsApp via Google Drive + Kommo (ver `docs/stories/story-h1-whatsapp-gdrive-kommo.md`)

### Pendente de decisão (bloqueadores da STORY-H-01)
1. ⏳ Validar estrutura exata das colunas da planilha com o Kommo/Make (Helder/Edilvo)
2. ⏳ Definir método de autenticação Google Drive: **Service Account JSON** (mais simples, uso interno) vs **OAuth** (necessário para SaaS futuro)

---

## Próxima Sessão — STORY-H-01

Após resolver os bloqueadores acima:

1. Migration `008_add_config_whatsapp` (nova tabela `config_whatsapp` por empresa)
2. Aba "WhatsApp" em Configurações (blocos: Google Drive + Kommo + Comportamento)
3. Botão "Exportar para WhatsApp" em Envio de Mensagens
4. Módulo `gdrive.py` — geração do XLSX + upload no Drive
5. Registro na tabela `envios` com `canal='whatsapp_crm'`
6. Testes em `tests/test_whatsapp.py`

---

## Histórico de Sessões

### Sessão 11/06/2026 — Brainstorm Fase H
- Brainstorm completo da Fase H com Helder
- Fluxo WhatsApp definido: App → Google Drive → Kommo → WhatsApp
- Decisão: geração sob demanda (botão em Envio de Mensagens), não automática
- Visão estratégica registrada: produto SaaS multi-tenant, Edilvo = cliente zero (laboratório)
- STORY-H-01 criada em `docs/stories/story-h1-whatsapp-gdrive-kommo.md`
- ROADMAP, MEMORY e PLANO atualizados
- Commit: `524da68`

### Sessão 10/06/2026 (noite)
- STORY-01-06 (Autenticação Flask-Login) ✅
- STORY-01-07 (First-run setup robusto) ✅ → **EPIC-01 COMPLETO**
- Central de Ajuda (`/ajuda`) ✅
- Gestão de múltiplos usuários (migration 007, `/usuarios`, `/conta`) ✅
- UI: cards de filtro uniformes (Base + Resultado) ✅
- UX: menu do usuário em dropdown no topbar ✅
- Suíte de testes pytest (49 testes, banco isolado) ✅
- Backup do banco com retenção (`backup_db.py`) ✅

### Sessão 10/06/2026 (tarde)
- STORY-01-03 (Loading states + confirmação Atualizar Base) ✅
- STORY-01-05 (Schema migrations + índices + WAL) ✅
- STORY-01-04 (Senha SMTP via Keyring) ✅
- Banco real de produção migrado (versionamento + WAL + senha no keyring)

### Sessão 10/06/2026 (manhã)
- Correções de UI (R1/R2/B1/B2) ✅
- STORY-01-01 (Quick Wins) ✅
- STORY-01-02 (Indicadores de empresa ativa) ✅
- STORY-01-07 adicionada ao backlog

---

## EPIC-01 — Sprint Zero ✅ COMPLETO (10/06/2026)

| Story | Título | Status |
|-------|--------|--------|
| 01-01 | Quick Wins — encoding, cores, títulos, confirmações, secret key | ✅ |
| 01-02 | Indicadores de empresa ativa (topbar + wizard) | ✅ |
| 01-03 | Loading states + confirmação "Atualizar Base" | ✅ |
| 01-04 | Proteger senha SMTP com Python Keyring | ✅ |
| 01-05 | Schema migrations + índices + WAL mode | ✅ |
| 01-06 | Autenticação Flask-Login (multi-usuário) | ✅ |
| 01-07 | First-run setup robusto | ✅ |

---

## Sprint H-1 — WhatsApp + Google Drive + Kommo 🔲

| Item | Status |
|------|--------|
| Definir colunas da planilha com Kommo/Make | ⏳ Pendente (Helder/Edilvo) |
| Definir método auth Google Drive | ⏳ Pendente |
| Migration `008_add_config_whatsapp` | 🔲 |
| Aba "WhatsApp" em Configurações | 🔲 |
| Botão "Exportar para WhatsApp" em Envio de Mensagens | 🔲 |
| Módulo `gdrive.py` (geração XLSX + upload) | 🔲 |
| Testes `test_whatsapp.py` | 🔲 |

## Sprint H-2 — Agendamento + Dashboard 🔲

| Item | Status |
|------|--------|
| Agendamento via Windows Task Scheduler | 🔲 |
| Dashboard analítico básico (evolução semanal, taxa de quitação) | 🔲 |

---

## Bloqueios

| # | Bloqueio | Responsável |
|---|---------|-------------|
| 1 | Validar formato das colunas com Kommo/Make | Helder/Edilvo |
| 2 | Definir método de auth Google Drive (Service Account vs OAuth) | Helder |
