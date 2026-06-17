# PLANO DE AÇÃO — MAT-INE Inadimplência 2026

> Sprint atual e próximos passos. Atualizar a cada sessão.
> Quando um item é entregue: marca ✅ aqui e registra no ROADMAP.md.
> Última atualização: 17/06/2026

---

## Estado Atual

- **Branch:** `homologacao`
- **Fase do produto:** Fases A–G + EPIC-01 (Sprint Zero) **100% concluídos**. Fase H em andamento — STORY-H-01 **completa em código** (status InReview): falta o onboarding real (Service Account + Shared Drive + teste com Kommo).
- **EPIC-02 CONCLUÍDO (Ondas 0–7):** app **no ar na nuvem via Render** — Helder confirmou acesso pela URL em 17/06. Web Service `matine-cobranca` (gunicorn `-w 2`, `rootDir=06_APP`) + Postgres gerenciado `matine-db` (`render.yaml`); env vars `DATABASE_URL`, `FLASK_SECRET_KEY` (gerada), `MATINE_DATA_DIR=/tmp/matine`, `APP_USUARIO/APP_SENHA`, `SMTP_INEPROTEC_SENHA`, `SMTP_MATRICULAEAD_SENHA`. App agora roda em Postgres na nuvem (validação real do dual-dialect). Suíte SQLite local: **90 verdes**.
- **App (local):** roda com `python app.py` em `06_APP/` → http://localhost:5000 (SQLite). Em nuvem: Render + Postgres.
- **A verificar (smoke test pós-deploy):** confirmar fluxo ponta a ponta no ar (login → upload → consolidar → relatório/CRM → envio) e **trocar a senha admin default**.

---

## O Que Está Pendente

### Pendente de implementação
- **STORY-H-01 — Onda 2 (UI + fluxo)** ✅ **ENTREGUE 15/06** — aba "WhatsApp" em Configurações (Drive + Kommo + Comportamento) + sublink, rotas `/whatsapp/configurar|testar|exportar`, botão Testar Conexão (AJAX), botão "Exportar para WhatsApp" em Envio de Mensagens, registro em `envios` (`canal='whatsapp_crm'`). +7 testes. **Falta só o onboarding real** (ver Próxima Sessão).
- **Submenu "Canais de Comunicação" + aba SMS** — reorganizar Configurações: agrupar E-mail (Fase G ✅), WhatsApp (H-1 ✅) e SMS (novo) sob um submenu "Canais de Comunicação". Inclui criar a aba de configuração de SMS (provider TBD). Ver Sprint H-3.

### Decisões dos bloqueadores da STORY-H-01 — ✅ RESOLVIDOS (15/06/2026)
1. ✅ **Formato da planilha:** reaproveitar a **Planilha CRM** existente (`proc.gerar_planilha_crm`), gerada em Envio de Mensagens → botão "Planilha CRM". XLSX com 2 abas: `Inadimplentes` (Nome, CPF, Telefone, E-mail, Categoria, Dias Atraso, Valor, Tag CRM) + `Saídos_Quitados`. O Kommo lê a aba `Inadimplentes` (Telefone + Tag CRM são o essencial).
2. ✅ **Auth Google Drive:** **Service Account** (JSON) + **Shared Drive** (Workspace confirmado). Arquivos pertencem à organização (não à SA) → sem `storageQuotaExceeded`. SA como membro Gerenciador de conteúdo; API com `supportsAllDrives=True`. OAuth fica para a v2 SaaS (cada tenant conecta o próprio Drive); `gdrive.py` modular para troca barata.

---

## Próxima Sessão (nova janela) — pós-deploy: validar no ar + onboarding Drive

> EPIC-02 concluído (Ondas 0–7); app no ar no Render (Helder confirmou acesso em 17/06).
> Foco agora: fechar pendências do deploy e retomar a Fase H.

**1. Smoke test pós-deploy (verificação do ambiente no ar):**
- Login → upload de base → consolidar → gerar relatório/Planilha CRM (download) → envio de e-mail teste.
- **Trocar a senha admin default** (`APP_USUARIO`/`APP_SENHA` no Render) por credencial real.
- Conferir logs do Render (stdout) e ausência de erro de dialeto/Postgres.

**2. STORY-H-01 — onboarding real do Google Drive (fecha a story, InReview → Done):**
criar Service Account + Shared Drive, montar o Secret File no Render (`GOOGLE_SA_{empresa}_JSON_PATH`),
testar conexão/exportação e validar com o Kommo → QA gate. Entradas: `configuracoes.html` (aba WhatsApp),
`envio_mensagens.html` (botão Exportar), rotas `/whatsapp/*` em `app.py`, `06_APP/gdrive.py`.

**3. Backlog Fase H (escolher com Helder):** Sprint H-2 (Agendamento + Dashboard analítico) ou
Sprint H-3 (submenu "Canais de Comunicação" + aba SMS).

---

## Histórico de Sessões

### Sessão 17/06/2026 — Validação do deploy + hardening de migrations concorrentes
- **Smoke test automático do Render:** app no ar (HTTP 200 após cold start ~30–60s do free tier), `/` → 302 `/login`, página "Login – Cobranças INE-MAT" OK, sem erro 500/Postgres. Falta a parte interativa (login/upload/consolidar/relatório/envio + **trocar senha admin default** — login padrão `luana/matine2026` em `app.py:1510`).
- **🔒 Race condition em migrations resolvido** (`06_APP/migrations/runner.py`): com `gunicorn -w 2`, os 2 workers chamam `init_db` no boot e podiam aplicar a mesma migration em paralelo (falha de PK em `schema_migrations`). Adicionados `acquire_lock`/`release_lock` (Postgres: `pg_advisory_lock` de sessão; SQLite: no-op) envolvendo `apply_pending` em try/finally. Agora 1 worker aplica e os demais esperam.
- **+2 testes** (`test_migrations.py`): `test_lock_noop_sqlite` (passa) + `test_advisory_lock_serializa_migrations` (pula sem `TEST_DIALECT=postgres`). **Suíte: 91 passed, 1 skipped.**
- Decisão formal (Modelo 1) sobre fluxo de gestão→commit→push, com comando `entregar`, gravada no CLAUDE.md global.
- **Como migrations chegam ao Postgres:** automático no boot — `setup_inicial()` roda no import (`app.py:361`), sob gunicorn; runner aplica só as pendentes, em ordem, atômicas. Regra: forward-only + cross-dialect (`ddl.py`) + testar em Postgres antes.

### Sessão 16/06/2026 — EPIC-02 Ondas 6 e 7 (testes dual-dialect + deploy Render) ✅ EPIC-02 CONCLUÍDO
- **Onda 6** (`cabf8c4`): conftest parametrizado (`TEST_DIALECT=postgres` sobe Postgres efêmero via testcontainers); `_tabelas()` cross-dialect em 3 arquivos de teste; `r['version']`/`r['cnt']`/`r['coluna']` no lugar de `r[0]`; 7 testes `sqlite_only` (raw `sqlite3.connect`, PRAGMA, backup SQLite). Suíte SQLite: 90 verdes.
- **Onda 7** (`e8325e3`): `render.yaml` (Web Service `matine-cobranca` python, `rootDir=06_APP`, `buildCommand=pip install -r requirements.txt`, `startCommand=gunicorn -w 2`); `06_APP/Procfile`; Postgres gerenciado `matine-db`; env vars (`DATABASE_URL` fromDatabase, `FLASK_SECRET_KEY` generateValue, `MATINE_DATA_DIR=/tmp/matine`, `APP_USUARIO/SENHA`, `SMTP_*_SENHA` sync:false); fixes postgres.
- **App no ar:** Helder confirmou acesso pela URL do Render em 17/06 → Postgres na nuvem valida o dual-dialect na prática.
- **Pendências pós-deploy:** smoke test ponta a ponta + trocar senha admin default (ver Próxima Sessão).
- Commits `cabf8c4` + `e8325e3` — **push concluído** em `origin/homologacao` (verificado: 0 ahead/0 behind).
- **Nota de sincronia (17/06):** PLANO/ROADMAP estavam uma onda atrás (commitados na Onda 6); reconciliados com o git nesta sessão.

### Sessão 16/06/2026 — EPIC-02 Onda 5 (segredos → env vars)
- **`app.py` `_env_get`**: agora lê `os.environ` primeiro e cai no `.env` local como fallback — sem isso, `FLASK_SECRET_KEY` regenerava a cada deploy no Render e desloga todos os usuários
- **`database.py` keyring blindado**: `_gravar_senha_smtp` e `_ler_senha_smtp` ignoram o keyring quando `DIALECT == 'postgres'` (skip + log); no local (SQLite), comportamento inalterado. SMTP na nuvem vem de `SMTP_{empresa}_SENHA` como env var
- **`database.py` Drive via Secret File**: `get_gdrive_credentials_path` lê `GOOGLE_SA_{empresa}_JSON_PATH` do `os.environ` antes de procurar `DATA_DIR/secrets/`; no Render, montar o Secret File e setar a env var é suficiente para o Drive funcionar
- **Suíte: 90 verdes** (nenhum teste afetado — lógica local/SQLite inalterada)

### Sessão 16/06/2026 — EPIC-02 Ondas 0–2 (dual-dialect)
- **Onda 0**: `requirements.txt` + `psycopg[binary]>=3.1.0` / `psycopg-pool>=3.1.0`; `DATABASE_URL`/`DIALECT` em `database.py` (import protegido — sem o pacote, SQLite segue funcionando)
- **Onda 1**: `_PGConn` wrapper (`?`→`%s`, `isolation_level.setter`→`autocommit`, context-manager); `get_conn()` ramifica SQLite↔Postgres via `_psycopg.connect(row_factory=dict_row)`; 4 COUNT aliases (`r[0]`→`r['cnt']`); `runner.py`: `r['version']`/`row['max_ver']`; `_IntegrityError` cross-dialect; `_table_exists` guarda Postgres. Fix de 2 testes que usavam `sqlite3.connect` raw sem `row_factory`
- **Onda 2**: `migrations/ddl.py` novo (`pk_int`, `blob`, `ts_default` — lê `DATABASE_URL` direto evitando import circular); runner: `sys.path` + `ddl.ts_default()` em `ensure_migrations_table`; migrations 001–010 com f-strings e `ddl.*`; 006 WAL guard sqlite; `database.py`: `INSERT OR IGNORE→ON CONFLICT DO NOTHING`, `lastrowid→RETURNING id`, 3× `datetime('now')→` param Python
- **Suíte: 90 verdes** (commits `629949b`, `7851765`, `e5561c8`; push em `origin/homologacao`)

### Sessão 15/06/2026 — EPIC-02 Onda 3 (matar o pickle)
- Revisão da spec do EPIC-02 (coerente, bem sequenciada) antes de implementar
- A pedido do Helder ("matar pickle e arquivos"), priorizada a Onda 3 fora da ordem 0→1→2
- **Migration 009** (`estado_consolidacao`: empresa PK, payload BLOB, atualizado_em) — cross-dialect (BLOB→BYTEA)
- **`database.py`**: `salvar_estado_blob` / `carregar_estado_blob` / `limpar_estado_blob` / `estado_existe` (`ON CONFLICT(empresa)`)
- **`app.py`**: `_salvar/_carregar/_limpar_estado` agora usam o blob no banco (mesmo `pickle.dumps/loads`); `sessao_ativa` via `db.estado_existe`; removidos `_estado_file`, `ESTADO_DIR` e a criação da pasta `estado/`
- **+8 testes** (`tests/test_estado.py`): round-trip, substituição, isolamento por empresa, limpeza, migração de categorias antigas, **nenhum `.pkl` em disco**. Asserções de lista de migrations (`test_migrations.py`, `test_whatsapp.py`) atualizadas p/ incluir a 009. **Suíte: 79 verdes.**
- Decisão: parar na Onda 3 e commitar; Onda 4 (stateless de arquivos) em sessão futura
- Estados `.pkl` legados em produção serão ignorados após deploy (estado é regenerável; dados persistentes ficam em `inadimplentes`)

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

## EPIC-02 — Cloud-Native Stateless (ponte para v2) ✅ CONCLUÍDO (16/06/2026, no ar no Render)

> Decidido 15/06/2026. Caminho B (stateless), Render, Postgres. Spec: `docs/stories/epic-02-cloud-native-stateless.md`. Esforço total ~30h (~3–4 janelas).

| Onda | Objetivo | Status |
|------|----------|--------|
| 0 | Deps (`psycopg`, `psycopg_pool`) + switch de dialeto (`DATABASE_URL`) sem uso | ✅ 16/06 |
| 1 | Wrapper conn/cursor + `get_conn()` ramifica + placeholders `?`→`%s` + acessos `[0]`→alias | ✅ 16/06 |
| 2 | Migrations cross-dialect (`ddl.py`, AUTOINCREMENT, `datetime`, `ON CONFLICT`, `RETURNING`) | ✅ 16/06 |
| 3 | Matar o pickle: estado → tabela `estado_consolidacao` (BLOB/BYTEA); `_salvar/_carregar/_limpar_estado` via `db.*_estado_blob` + `estado_existe`; +8 testes | ✅ 15/06 |
| 4 | Stateless de arquivos: upload → staging (migration 010) lido em memória + relatórios/CRM via download (ZIP/xlsx) + remover `os.startfile`/`/abrir-relatorios` + logs stdout; +13 testes | ✅ 16/06 |
| 5 | Segredos → env vars + Secret File do Drive; blindar keyring | ✅ 16/06 |
| 6 | Testes dual-dialect (conftest parametrizado + Postgres efêmero) | ✅ 16/06 |
| 7 | Deploy Render (Web Service + Postgres + env + Procfile/render.yaml) — **no ar 16/06** | ✅ 16/06 |

---

## Bloqueios

| # | Bloqueio | Responsável | Status |
|---|---------|-------------|--------|
| 1 | Validar formato das colunas com Kommo/Make | Helder/Edilvo | ✅ Resolvido 15/06 — reusa Planilha CRM |
| 2 | Definir método de auth Google Drive (Service Account vs OAuth) | Helder | ✅ Resolvido 15/06 — Service Account + Shared Drive (Workspace) |

> Nenhum bloqueador ativo. STORY-H-01 liberada para implementação.
