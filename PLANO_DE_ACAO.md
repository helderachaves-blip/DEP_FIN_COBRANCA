# PLANO DE AÇÃO — MAT-INE Inadimplência 2026

> Sprint atual e próximos passos. Atualizar a cada sessão.
> Quando um item é entregue: marca ✅ aqui e registra no ROADMAP.md.
> Última atualização: 15/06/2026

---

## Estado Atual

- **Branch:** `homologacao`
- **Fase do produto:** Fases A–G + EPIC-01 (Sprint Zero) **100% concluídos**. Fase H em andamento — STORY-H-01 **completa em código** (status InReview): falta o onboarding real (Service Account + Shared Drive + teste com Kommo).
- **Decisão estratégica 15/06/2026 (esta sessão):** disponibilizar o app por **URL** para o Edilvo/Luana validarem → escolhido o **Caminho B — Cloud-Native Stateless** (ponte para a v2), host **Render**, banco **PostgreSQL gerenciado**. Plano detalhado em `docs/stories/epic-02-cloud-native-stateless.md`. **Nenhum código alterado ainda** — implementação começa na próxima janela.
- **Pendente de push:** (preencher após o commit desta sessão — verificar contra `origin/homologacao`).
- **App (hoje):** roda com `python app.py` em `06_APP/` → http://localhost:5000. Estrutura `C:\MATINE` criada automaticamente no startup.

---

## O Que Está Pendente

### Pendente de implementação
- **STORY-H-01 — Onda 2 (UI + fluxo)** ✅ **ENTREGUE 15/06** — aba "WhatsApp" em Configurações (Drive + Kommo + Comportamento) + sublink, rotas `/whatsapp/configurar|testar|exportar`, botão Testar Conexão (AJAX), botão "Exportar para WhatsApp" em Envio de Mensagens, registro em `envios` (`canal='whatsapp_crm'`). +7 testes. **Falta só o onboarding real** (ver Próxima Sessão).
- **Submenu "Canais de Comunicação" + aba SMS** — reorganizar Configurações: agrupar E-mail (Fase G ✅), WhatsApp (H-1 ✅) e SMS (novo) sob um submenu "Canais de Comunicação". Inclui criar a aba de configuração de SMS (provider TBD). Ver Sprint H-3.

### Decisões dos bloqueadores da STORY-H-01 — ✅ RESOLVIDOS (15/06/2026)
1. ✅ **Formato da planilha:** reaproveitar a **Planilha CRM** existente (`proc.gerar_planilha_crm`), gerada em Envio de Mensagens → botão "Planilha CRM". XLSX com 2 abas: `Inadimplentes` (Nome, CPF, Telefone, E-mail, Categoria, Dias Atraso, Valor, Tag CRM) + `Saídos_Quitados`. O Kommo lê a aba `Inadimplentes` (Telefone + Tag CRM são o essencial).
2. ✅ **Auth Google Drive:** **Service Account** (JSON) + **Shared Drive** (Workspace confirmado). Arquivos pertencem à organização (não à SA) → sem `storageQuotaExceeded`. SA como membro Gerenciador de conteúdo; API com `supportsAllDrives=True`. OAuth fica para a v2 SaaS (cada tenant conecta o próprio Drive); `gdrive.py` modular para troca barata.

---

## Próxima Sessão (nova janela) — EPIC-02 Cloud-Native Stateless: Onda 0 + Onda 1

Iniciar a implementação do **EPIC-02** (`docs/stories/epic-02-cloud-native-stateless.md`).
Caminho B (stateless), host Render, Postgres gerenciado, modelo de 2 empresas mantido.

1. **Onda 0 — Preparação (~0,5h):** adicionar `psycopg[binary]` + `psycopg_pool` ao
   `requirements.txt`; introduzir o switch de dialeto (`DATABASE_URL`/`DIALECT`) em `database.py`
   **sem usá-lo ainda**. SQLite continua 100% — suíte verde.
2. **Onda 1 — Wrapper + placeholders (~5h):** wrapper conn/cursor unificado; `get_conn()` ramifica
   (SQLite como hoje / Postgres via `psycopg_pool` + `dict_row`); helper `?`→`%s`; padronizar
   acessos posicionais `[0]`→alias (`database.py:484,521,706,793`; `runner.py:37,42`).
   Validar SQLite verde após cada passo.

> **Estratégia dual-dialect:** SQLite em dev/testes (rápido, zero infra) + Postgres na nuvem,
> selecionado por `DATABASE_URL`. Rollback trivial; preserva os ~91 testes locais.

**Pendência paralela (não bloqueia o EPIC-02) — STORY-H-01 onboarding real:** criar Service
Account + Shared Drive, testar conexão/exportação e validar com o Kommo → QA gate (InReview → Done).
Helder fará quando o ambiente estiver no ar. Entradas: `configuracoes.html` (aba WhatsApp),
`envio_mensagens.html` (botão Exportar), rotas `/whatsapp/*` em `app.py`, `06_APP/gdrive.py`.

---

## Histórico de Sessões

### Sessão 15/06/2026 (planejamento) — Estratégia de disponibilização + EPIC-02
- Pergunta de partida: como disponibilizar o app para o Edilvo/Luana validarem (deploy/versionamento/local)
- Esclarecido: versionamento ≠ deploy ≠ disponibilização; "acessível por várias máquinas" = 1 URL (não exige multi-instância); Vercel descartada (serverless não serve Flask/pandas com estado)
- Investigação completa (3 Explore agents): camada SQLite, acoplamentos com filesystem/keyring/pickle, multi-tenancy hardcoded (2 empresas)
- Decisão: **Caminho B — Cloud-Native Stateless**, host **Render**, **Postgres** gerenciado; modelo de 2 empresas mantido (multi-tenant fica para v2)
- Plano detalhado em 8 ondas criado em `docs/stories/epic-02-cloud-native-stateless.md` (~30h)
- **Sem alteração de código** — só gestão + spec. Implementação inicia na próxima janela (Ondas 0–1)
- PLANO, MEMORY e ROADMAP atualizados

### Sessão 15/06/2026 (continuação) — Onda 2 da STORY-H-01 (UI + fluxo)
- **Aba "WhatsApp" em Configurações** (blocos Google Drive + Kommo + Comportamento) + sublink na sidebar
- **Rotas novas em `app.py`:** `/whatsapp/configurar` (upload do JSON com validação),
  `/whatsapp/testar` (AJAX → JSON, chama `gdrive.testar_conexao`),
  `/whatsapp/exportar` (gera Planilha CRM → `gdrive.upload_xlsx` → registra `envios` canal `whatsapp_crm`)
- **Botão "Exportar para WhatsApp"** em Envio de Mensagens (só aparece quando o Drive está configurado)
- **Botão Testar Conexão** (AJAX, padrão SMTP) com feedback inline
- Credencial nunca renderizada no HTML (AC) — coberto por teste de regressão
- **+7 testes de rota** em `test_whatsapp.py`. **Suíte: 71 verdes.**
- Limpeza: `wizard_whatsapp.html` (órfão, não referenciado) movido para `UTILITARIOS/TEMP/`
- Story H-01 → InReview; PLANO, ROADMAP e story atualizados
- Commits `440ccfc` (Onda 2) + `24ed9fc` (sincronia) — **push concluído** por @devops (`d93bc4b..24ed9fc`)
- Onboarding real (SA + Shared Drive + teste com Kommo) — Helder fará depois

### Sessão 15/06/2026 — Destrava + Onda 1 da STORY-H-01
- Bloqueador #1 (formato da planilha) resolvido: reaproveitar a Planilha CRM existente
- Bloqueador #2 (auth Drive) resolvido: Service Account + Shared Drive (Workspace confirmado)
- Sprint H-3 (Canais de Comunicação + SMS) adicionado ao plano/roadmap (SMS provider TBD)
- **STORY-H-01 Onda 1 (fundação backend) implementada:** migration 008 (`config_whatsapp`),
  `gdrive.py` (SA + Shared Drive, modular), helpers no `database.py` (credencial em `secrets/`),
  libs Google no `requirements.txt`, `tests/test_whatsapp.py` (12 testes). **Suíte: 64 verdes.**
- Story → InProgress; PLANO, MEMORY e ROADMAP atualizados
- Commit `c529919` + push para `origin/homologacao` (verificado, sincronizado)

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
| Definir colunas da planilha com Kommo/Make | ✅ Resolvido (reusa Planilha CRM) |
| Definir método auth Google Drive | ✅ Resolvido (Service Account + Shared Drive) |
| Migration `008_add_config_whatsapp` | ✅ Onda 1 |
| Módulo `gdrive.py` (upload + testar conexão) | ✅ Onda 1 |
| `database.py` config_whatsapp + credencial em `secrets/` | ✅ Onda 1 |
| Testes `test_whatsapp.py` (12 testes) | ✅ Onda 1 |
| Aba "WhatsApp" em Configurações + rotas | ✅ Onda 2 |
| Botão Testar Conexão (AJAX → `gdrive.testar_conexao`) | ✅ Onda 2 |
| Botão "Exportar para WhatsApp" em Envio de Mensagens | ✅ Onda 2 |
| Registro em `envios` (`canal='whatsapp_crm'`) | ✅ Onda 2 |
| Testes de rota (`test_whatsapp.py`, +7) | ✅ Onda 2 |
| Onboarding real (SA + Shared Drive + teste com Kommo) | 🔲 Próxima sessão |

## Sprint H-2 — Agendamento + Dashboard 🔲

| Item | Status |
|------|--------|
| Agendamento via Windows Task Scheduler | 🔲 |
| Dashboard analítico básico (evolução semanal, taxa de quitação) | 🔲 |

## Sprint H-3 — Canais de Comunicação + SMS 🔲

> Reorganização de UX em Configurações: agrupar os canais sob um submenu único.

| Item | Status |
|------|--------|
| Submenu **"Canais de Comunicação"** em Configurações (agrupa E-mail + WhatsApp + SMS) | 🔲 |
| Mover aba **E-mail** (existente) para dentro do submenu | 🔲 |
| Mover aba **WhatsApp** (criada na H-1) para dentro do submenu | 🔲 |
| Nova aba **SMS** — config de provider (provider TBD: Twilio / Zenvia / Comtele etc.) | 🔲 |
| Envio SMS individual + em lote + registro em `envios` (`canal='sms'`) | 🔲 |

---

## EPIC-02 — Cloud-Native Stateless (ponte para v2) 🔲

> Decidido 15/06/2026. Caminho B (stateless), Render, Postgres. Spec: `docs/stories/epic-02-cloud-native-stateless.md`. Esforço total ~30h (~3–4 janelas).

| Onda | Objetivo | Status |
|------|----------|--------|
| 0 | Deps (`psycopg`, `psycopg_pool`) + switch de dialeto (`DATABASE_URL`) sem uso | 🔲 Próxima sessão |
| 1 | Wrapper conn/cursor + `get_conn()` ramifica + placeholders `?`→`%s` + acessos `[0]`→alias | 🔲 Próxima sessão |
| 2 | Migrations cross-dialect (`ddl.py`, AUTOINCREMENT, `datetime`, `ON CONFLICT`, `RETURNING`) | 🔲 |
| 3 | Matar o pickle: estado → tabela `estado_consolidacao` (BYTEA) no Postgres | 🔲 |
| 4 | Stateless de arquivos: upload em memória + relatórios via download (ZIP) + remover `os.startfile` + logs stdout | 🔲 |
| 5 | Segredos → env vars + Secret File do Drive; blindar keyring | 🔲 |
| 6 | Testes dual-dialect (conftest parametrizado + Postgres efêmero) | 🔲 |
| 7 | Deploy Render (Web Service + Postgres + env + Procfile/runtime) + smoke test | 🔲 |

---

## Bloqueios

| # | Bloqueio | Responsável | Status |
|---|---------|-------------|--------|
| 1 | Validar formato das colunas com Kommo/Make | Helder/Edilvo | ✅ Resolvido 15/06 — reusa Planilha CRM |
| 2 | Definir método de auth Google Drive (Service Account vs OAuth) | Helder | ✅ Resolvido 15/06 — Service Account + Shared Drive (Workspace) |

> Nenhum bloqueador ativo. STORY-H-01 liberada para implementação.
