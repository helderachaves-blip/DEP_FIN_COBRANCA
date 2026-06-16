# PLANO DE AÇÃO — MAT-INE Inadimplência 2026

> Sprint atual e próximos passos. Atualizar a cada sessão.
> Quando um item é entregue: marca ✅ aqui e registra no ROADMAP.md.
> Última atualização: 16/06/2026

---

## Estado Atual

- **Branch:** `homologacao`
- **Fase do produto:** Fases A–G + EPIC-01 (Sprint Zero) **100% concluídos**. Fase H em andamento — STORY-H-01 **completa em código** (status InReview): falta o onboarding real (Service Account + Shared Drive + teste com Kommo).
- **EPIC-02 em implementação:** **Ondas 3 e 4 entregues.** Onda 3 (15/06) matou o pickle (estado → blob no banco, migration 009). **Onda 4 (16/06)** tornou os arquivos stateless: upload → staging no banco (migration 010, `uploads_staging`), consolidação/atualização lendo em memória (`BytesIO`), relatórios/CRM via **download** (ZIP/xlsx), `os.startfile` e `/abrir-relatorios` removidos, `_log` → stdout. Suíte: **90 verdes** (+13 em `test_uploads.py`). Ondas 0–2 (dual-dialect) ainda não feitas; tudo roda em SQLite hoje e fica pronto para Postgres (BLOB→BYTEA na Onda 2).
- **Pendente de push:** nada — Onda 4 (feat `65bf8c3`) em `origin/homologacao` (push `1365447..65bf8c3` por @devops; `git fetch` confirma 0 ahead/0 behind).
- **App (hoje):** roda com `python app.py` em `06_APP/` → http://localhost:5000. Só `logs\` e `banco\` (SQLite) usam disco local; uploads/relatórios não tocam mais o filesystem.

---

## O Que Está Pendente

### Pendente de implementação
- **STORY-H-01 — Onda 2 (UI + fluxo)** ✅ **ENTREGUE 15/06** — aba "WhatsApp" em Configurações (Drive + Kommo + Comportamento) + sublink, rotas `/whatsapp/configurar|testar|exportar`, botão Testar Conexão (AJAX), botão "Exportar para WhatsApp" em Envio de Mensagens, registro em `envios` (`canal='whatsapp_crm'`). +7 testes. **Falta só o onboarding real** (ver Próxima Sessão).
- **Submenu "Canais de Comunicação" + aba SMS** — reorganizar Configurações: agrupar E-mail (Fase G ✅), WhatsApp (H-1 ✅) e SMS (novo) sob um submenu "Canais de Comunicação". Inclui criar a aba de configuração de SMS (provider TBD). Ver Sprint H-3.

### Decisões dos bloqueadores da STORY-H-01 — ✅ RESOLVIDOS (15/06/2026)
1. ✅ **Formato da planilha:** reaproveitar a **Planilha CRM** existente (`proc.gerar_planilha_crm`), gerada em Envio de Mensagens → botão "Planilha CRM". XLSX com 2 abas: `Inadimplentes` (Nome, CPF, Telefone, E-mail, Categoria, Dias Atraso, Valor, Tag CRM) + `Saídos_Quitados`. O Kommo lê a aba `Inadimplentes` (Telefone + Tag CRM são o essencial).
2. ✅ **Auth Google Drive:** **Service Account** (JSON) + **Shared Drive** (Workspace confirmado). Arquivos pertencem à organização (não à SA) → sem `storageQuotaExceeded`. SA como membro Gerenciador de conteúdo; API com `supportsAllDrives=True`. OAuth fica para a v2 SaaS (cada tenant conecta o próprio Drive); `gdrive.py` modular para troca barata.

---

## Próxima Sessão (nova janela) — EPIC-02: Ondas 0–2 (dual-dialect) ou Onda 5 (segredos)

> Com as Ondas 3 e 4 prontas, o app está **stateless** (banco + downloads, sem disco de
> operação). O que falta para o deploy no Render é tornar o banco **dual-dialect** (Postgres)
> e mover segredos para env vars. Ordem livre antes da Onda 7 (deploy).

**Ondas 0–2 — Dual-dialect (~10h):** SQLite em dev/testes + Postgres na nuvem por `DATABASE_URL`.
- **Onda 0** — deps (`psycopg[binary]`, `psycopg_pool`) + switch de dialeto sem uso.
- **Onda 1** — wrapper conn/cursor; `get_conn()` ramifica + pool PG; placeholders `?`→`%s`;
  acessos posicionais `[0]`→alias. As migrations 009/010 já usam `ON CONFLICT` e BLOB.
- **Onda 2** — migrations cross-dialect (`ddl.py`, AUTOINCREMENT→IDENTITY, `datetime`→
  `CURRENT_TIMESTAMP`, `RETURNING`, BLOB→BYTEA).

**Onda 5 — Segredos → env (~2h):** `_env_get` prioriza `os.environ`; SMTP via env; Drive via
Secret File; blindar `keyring.set_password` (não quebrar sem o keyring do Windows).

**Pendência paralela (não bloqueia o EPIC-02) — STORY-H-01 onboarding real:** criar Service
Account + Shared Drive, testar conexão/exportação e validar com o Kommo → QA gate (InReview → Done).
Helder fará quando o ambiente estiver no ar. Entradas: `configuracoes.html` (aba WhatsApp),
`envio_mensagens.html` (botão Exportar), rotas `/whatsapp/*` em `app.py`, `06_APP/gdrive.py`.

---

## Histórico de Sessões

### Sessão 16/06/2026 — EPIC-02 Onda 4 (stateless de arquivos)
- Discussão prévia: disco persistente no Render (pago, prende a 1 instância, contraria
  "não guardar arquivos do cliente") vs **staging no banco** (escolhido — custo zero, preserva
  a tela da Luana, funciona entre workers). Confirmado que relatórios via download e remoção
  do `os.startfile` são obrigatórios para qualquer deploy web, independente de disco.
- **Migration 010** (`uploads_staging`: empresa+tipo PK, filename, conteudo BLOB) — cross-dialect.
- **`database.py`**: `salvar/carregar/limpar_upload_staging` + `status_uploads_staging` (`ON CONFLICT`).
- **`processing.py`**: `_ler_csv` aceita `Path` **ou** `(BytesIO, filename)`; helper `_fonte_nome`
  para mensagens de erro. Backward-compatible (testes que passam Path seguem verdes).
- **`app.py`**: `/upload` grava bytes no staging (valida extensão, sem disco); `_fonte_upload`
  substitui `_detectar_arquivo`; `/consolidar` e `/atualizar-base` leem em memória; `/gerar-relatorio`
  e `/crm/gerar-planilha` geram em tmp e **devolvem download** (ZIP/xlsx), tmp apagado no `finally`;
  `/whatsapp/exportar` usa tmp; removidos `os.startfile`, `/abrir-relatorios`, `_pasta_relatorio`,
  `UPLOADS_DIR/RELATORIOS/CRM_PASTA`; `_log` → stdout (arquivo só local via `EM_NUVEM`).
- **Templates**: index/resultado/configuracoes ajustados (presença por filename, botões de download
  sem `data-loading`, card "Abrir Relatórios" removido). README e MEMORY atualizados (estrutura local).
- **Decisão registrada**: `/atualizar-base` não grava mais TXT/XLSX de novos/saídos em disco
  (info segue no flash + tela Base). Reexport por download é candidato de v.next.
- **+13 testes** (`tests/test_uploads.py`): migration 010 up/down, staging round-trip/substituição/
  isolamento/status/limpeza, `_ler_csv` de buffer, e rota ponta a ponta (upload→staging→consolidar→ZIP).
  Asserções de lista de migrations (`test_migrations.py`, `test_whatsapp.py`) atualizadas p/ a 010.
  **Suíte: 90 verdes.**
- Decisão: parar na Onda 4 e commitar; próximo são Ondas 0–2 (dual-dialect) e/ou Onda 5 (segredos)

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

## EPIC-02 — Cloud-Native Stateless (ponte para v2) 🔲

> Decidido 15/06/2026. Caminho B (stateless), Render, Postgres. Spec: `docs/stories/epic-02-cloud-native-stateless.md`. Esforço total ~30h (~3–4 janelas).

| Onda | Objetivo | Status |
|------|----------|--------|
| 0 | Deps (`psycopg`, `psycopg_pool`) + switch de dialeto (`DATABASE_URL`) sem uso | ✅ 16/06 |
| 1 | Wrapper conn/cursor + `get_conn()` ramifica + placeholders `?`→`%s` + acessos `[0]`→alias | ✅ 16/06 |
| 2 | Migrations cross-dialect (`ddl.py`, AUTOINCREMENT, `datetime`, `ON CONFLICT`, `RETURNING`) | 🔲 |
| 3 | Matar o pickle: estado → tabela `estado_consolidacao` (BLOB/BYTEA); `_salvar/_carregar/_limpar_estado` via `db.*_estado_blob` + `estado_existe`; +8 testes | ✅ 15/06 |
| 4 | Stateless de arquivos: upload → staging (migration 010) lido em memória + relatórios/CRM via download (ZIP/xlsx) + remover `os.startfile`/`/abrir-relatorios` + logs stdout; +13 testes | ✅ 16/06 |
| 5 | Segredos → env vars + Secret File do Drive; blindar keyring | 🔲 Próxima |
| 6 | Testes dual-dialect (conftest parametrizado + Postgres efêmero) | 🔲 |
| 7 | Deploy Render (Web Service + Postgres + env + Procfile/runtime) + smoke test | 🔲 |

---

## Bloqueios

| # | Bloqueio | Responsável | Status |
|---|---------|-------------|--------|
| 1 | Validar formato das colunas com Kommo/Make | Helder/Edilvo | ✅ Resolvido 15/06 — reusa Planilha CRM |
| 2 | Definir método de auth Google Drive (Service Account vs OAuth) | Helder | ✅ Resolvido 15/06 — Service Account + Shared Drive (Workspace) |

> Nenhum bloqueador ativo. STORY-H-01 liberada para implementação.
