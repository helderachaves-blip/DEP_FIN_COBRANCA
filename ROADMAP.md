# ROADMAP — MAT-INE Inadimplência 2026

> Linha do tempo completa. Itens entregues nunca são deletados — apenas marcados ✅.
> Última atualização: 18/06/2026

---

## ✅ FASE A — UX Rápidos (03/06/2026)

- [x] Alinhamento `text-end` + `text-nowrap` nas colunas de valores
- [x] Importação de Alunos movida para Configurações
- [x] Botão "Limpar Base" com modal de confirmação (digitar "LIMPAR")
- [x] Aviso de alunos sem cadastro após consolidação (flash warning)
- [x] Pastas de mês com nome por extenso: `01-Janeiro` … `12-Dezembro`

---

## ✅ FASE B — Redesign Layout Sidebar (03/06/2026)

- [x] Sidebar escura (`#1a1a2e`) substituindo navbar horizontal
- [x] "Cobranças INE-MAT" no topo da sidebar
- [x] Topbar com logos Ineprotec (esq) e Matrícula EaD (dir) com opacidade dinâmica

---

## ✅ FASE C — Categorias + Filtros Dinâmicos (03/06/2026)

- [x] 3 categorias por dias de atraso: Novos (1d) · Régua (2–29d) · Acima 30 Dias (30d+)
- [x] Cards de filtro clicáveis em Resultado (JS filtra + atualiza totalizadores)
- [x] Migração automática de estado pickle com categorias antigas (A/B)

---

## ✅ FASE D — Multi-empresa (03/06/2026)

- [x] Toggle `[Ineprotec | Mat. EaD]` na topbar
- [x] PK composta `(cpf, empresa)` na tabela `inadimplentes`
- [x] Templates padrão duplicados por empresa
- [x] Uploads e relatórios separados por empresa
- [x] Migração automática: dados existentes preservados como INEPROTEC

---

## ✅ FASE E — Régua de Cobranças + Arquivo À Vencer (04/06/2026)

- [x] Processamento do arquivo AVENCER — card laranja + tabela "A Vencer" em Resultado
- [x] Placeholder `{LINK_PAGAMENTO}` nos templates (preenchimento manual no TXT)
- [x] Campo `qtd_cobranca` no banco — incrementa a cada relatório gerado
- [x] Coluna "Cobr." na tela Base
- [x] Nova aba "Régua" em Configurações
- [x] Estrutura `C:\MATINE\` criada automaticamente no startup
- [x] Submenu de Configurações na sidebar

---

## ✅ FASE F — Wizard de Envio WhatsApp (04/06/2026)

- [x] Tela `/envio-mensagens` com todas as mensagens formatadas
- [x] Botão "Copiar" por linha + expansão inline da mensagem
- [x] Barra de progresso: X/Y enviados + percentual
- [x] Marcar enviado por aluno (AJAX, sem reload)
- [x] Botão "Marcar Todos Enviados"
- [x] Tabela `envios` no banco (base para rastreamento por canal)
- [x] Filtro por categoria + busca por nome/telefone + ocultar enviados

---

## ✅ FASE G — Cobranças por E-mail (04/06/2026)

- [x] Configuração SMTP por empresa (host, port, usuário, senha, TLS)
- [x] Teste de conexão SMTP na tela de Configurações
- [x] Envio individual por aluno (AJAX)
- [x] Envio em lote para todos com e-mail cadastrado
- [x] Campo `assunto_email` nos templates
- [x] Registro de envios na tabela `envios` (canal='email')

---

## ✅ MUDANÇAS 1–5 — UX e CRM (08/06/2026)

- [x] Aba Resultado: removidos 4 botões redundantes (mantém só "Gerar Relatórios")
- [x] Após gerar relatório → redireciona para `/resultado` (não mais para envio de mensagens)
- [x] `wizard_whatsapp` renomeado para `envio_mensagens` em todo o código
- [x] Campo `tag_crm` nos templates + botão "Planilha CRM" em Envio de Mensagens
- [x] Aba Base: 4 cards de filtro rápido com lógica correta:
  - Novos Inadimplentes (`categoria = 'Novos Inadimplentes'`)
  - Em Renegociação (CPF presente no arquivo À Vencer da sessão)
  - Inadimplentes Gerais (`status = INADIMPLENTE` e não é Novo)
  - Inadimplentes Quitados (`status = QUITADO`)

---

## ✅ CORREÇÕES DE UI — Resultados + Base (10/06/2026)

Ajustes reportados pelo Edilvo na revisão do app. Apenas template + JS, sem backend.

- [x] **R1** — Cards "Vence Hoje" / "À Vencer" (Resultados) com auto-filtro, igual aos demais cards. Filtro estendido para a tabela "A Vencer" separada, com toggle de seção.
- [x] **R2** — Dropdown Filtrar de Resultados com as 5 categorias (Vence Hoje + A Vencer incluídas).
- [x] **B1** — Removidas as legendas INADIMPLENTE / QUITADO / RENEGOCIADO da aba Base.
- [x] **B2** — Dropdown Filtrar da Base com 5 categorias; "Vence Hoje"/"A Vencer" filtram pelas flags de sessão À Vencer.

---

## ✅ STORY-01-01 — Quick Wins (10/06/2026)

Primeira story do EPIC-01 entregue. 2 dos 5 itens já estavam satisfeitos pelo estado do app.

- [x] Encoding UTF-8 sem BOM (já OK em todos os templates)
- [x] Cores semânticas por categoria em Resultado e Envio de Mensagens (já OK)
- [x] Título dinâmico por página via `{% block title %}` (layout + 5 templates)
- [x] Confirmação modal antes de "Limpar Sessão" (não afeta a Base)
- [x] `secret_key` Flask gerada uma vez e persistida em `.env` (gitignored, sem dependência nova)

---

## ✅ STORY-01-02 — Indicadores de Empresa Ativa (10/06/2026)

- [x] Nome da empresa colorido na topbar (azul Ineprotec · verde Mat. EaD), acima do toggle
- [x] Banner "Enviando para: [EMPRESA]" no topo do wizard de envio
- [x] Confirmação ao trocar de empresa quando há consolidação ativa (flag `sessao_ativa`)

---

## ✅ STORY-01-03 — Loading States e Confirmação Atualizar Base (10/06/2026)

- [x] Handler global reutilizável em `layout.html`: todo `<form data-loading>` desabilita o botão de submit e troca o texto por spinner (`data-loading-text`), impedindo duplo clique
- [x] Loading state aplicado a: Consolidar, Gerar Relatórios (Início + Resultado), Atualizar Base, Importar Alunos, Salvar SMTP, Testar Conexão SMTP
- [x] Modal de confirmação antes de "Comparar e Atualizar Base" (`#modalAtualizarBase`, padrão consistente com Limpar Sessão/Limpar Base)
- [x] Flash de `/gerar-relatorio` com contagem total: "X mensagens prontas para envio"

---

## ✅ STORY-01-05 — Schema Migrations + Índices + WAL (10/06/2026)

Fundação de versionamento de banco — maior bloqueador técnico para a Fase H.

- [x] Tabela `schema_migrations` (version, name, applied_at)
- [x] `init_db()` refatorado de 163 linhas com 7 fases inline → runner que aplica só migrations pendentes
- [x] Diretório `06_APP/migrations/` com `runner.py` + scripts 001–006 (cada um com `up`/`down`)
- [x] Migrations atômicas (BEGIN/COMMIT por script); WAL como migration não-transacional
- [x] 5 índices de performance por `empresa` (migration 005)
- [x] WAL mode + `foreign_keys=ON` em `get_conn()` (leituras concorrentes — necessário p/ Fase H)
- [x] Detecção de banco legado: 001–004 marcadas como aplicadas sem re-executar
- [x] Banco real de produção migrado sem perda de dados (1024 inadimplentes; backup criado)

---

## ✅ STORY-01-04 — Senha SMTP Segura (keyring) (10/06/2026)

Senha SMTP fora do banco — fecha exposição em backups/cópias do `inadimplencia.db`.

- [x] `keyring>=25.0.0` (backend WinVaultKeyring = Windows Credential Manager)
- [x] `salvar_config_email` grava no keyring; coluna `smtp_senha` guarda só `[keyring]`
- [x] `get_config_email` lê do keyring (fallback: env `SMTP_<EMPRESA>_SENHA` → coluna legado)
- [x] Migração de segurança no startup: senha em texto plano → keyring (banco real migrado)
- [x] UI não vaza a senha no HTML; bullets quando configurada; campo vazio preserva a atual
- [x] Caminho de envio/teste SMTP inalterado (consome `config['smtp_senha']`)

---

## ✅ STORY-01-06 — Autenticação Flask-Login (10/06/2026)

Fecha o vetor de acesso aberto — pré-requisito de segurança para a Fase H (webhooks).

- [x] `flask-login>=0.6.3` + usuário único via `.env` (`APP_USUARIO`/`APP_SENHA`)
- [x] Senha como hash pbkdf2 (`werkzeug.security`) — nunca em texto plano
- [x] Login/logout funcionais; `remember=True` com cookie de 7 dias
- [x] Proteção de todas as rotas via guard global `before_request` (default-deny; allowlist login/logout/static) — novas rotas já nascem protegidas
- [x] Tela `login.html` standalone (logos, centralizada, sem sidebar) + footer da sidebar com usuário e botão Sair
- [x] Seed de fábrica `luana` / `matine2026` na 1ª execução (troca via `.env.example`)
- [x] Smoke test (Flask test client): 8/8 PASS, incluindo bloqueio de open-redirect

---

## ✅ STORY-01-07 — First-run setup robusto (10/06/2026)

Onboarding à prova de falhas — **fecha o EPIC-01**.

- [x] `setup_inicial()` idempotente encapsula a criação da estrutura (antes solta no import)
- [x] Passos: estrutura `C:\MATINE` → `db.init_db()` (schema + templates) → validação de deps
- [x] `_checar_dependencias()` — mensagem amigável (`pip install -r requirements.txt`) sem stack trace cru
- [x] Detecção de 1ª execução (ausência do banco) + sinalização no log e no banner
- [x] `06_APP/README.md` reescrito com onboarding web atual (era da versão desktop antiga)

---

## ✅ EPIC-01 — Sprint Zero (Pré-Fase H) — COMPLETO (10/06/2026)

Resolução de débitos técnicos críticos identificados no Brownfield Discovery.
**Pré-requisito para a Fase H — agora satisfeito (7/7 stories).**

| Story | Título | Esforço | Status |
|-------|--------|---------|--------|
| 01-01 | Quick Wins — encoding, cores, títulos, confirmações, secret key | ~7h | ✅ 10/06 |
| 01-02 | Indicadores de empresa ativa (topbar + wizard) | ~3h | ✅ 10/06 |
| 01-03 | Loading states + confirmação "Atualizar Base" | ~5h | ✅ 10/06 |
| 01-04 | Proteger senha SMTP com Python Keyring | ~4h | ✅ 10/06 |
| 01-05 | Schema migrations + índices + WAL mode | ~12h | ✅ 10/06 |
| 01-06 | Autenticação Flask-Login (MVP) | ~6h | ✅ 10/06 |
| 01-07 | First-run setup robusto (estrutura `C:\MATINE` + onboarding dev) | ~3h | ✅ 10/06 |

---

## ✅ Central de Ajuda (10/06/2026)

Suporte embutido no sistema — reduz dependência de Edilvo/Helder para dúvidas da operadora.

- [x] Rota `/ajuda` (protegida pelo login) + link "Ajuda" na sidebar (seção Suporte)
- [x] Página com índice lateral fixo + conteúdo por tela (ScrollSpy realça a seção ativa)
- [x] Conteúdo operacional passo a passo: Visão geral, Início, Resultado, Envio de Mensagens,
  Base, Configurações + Dúvidas frequentes
- [x] Responsivo (índice some em telas estreitas); manutenção documentada na story
- [x] **Atualização 18/06:** nova seção **Dashboard** (H-2) + bloco **Canais de Comunicação**
  em Configurações (E-mail/WhatsApp/SMS, H-1/H-3) — Ajuda sincronizada com as telas entregues.
  *(Pendente: prints das telas — ver INSIGHTS → Documentação)*

---

## ✅ Gestão de Múltiplos Usuários (10/06/2026)

Evolução da autenticação de usuário único (STORY-01-06) para multi-usuário no banco.

- [x] Migration `007_add_usuarios` — tabela `usuarios` (login único, nome, hash, is_admin, ativo)
- [x] Autenticação migrada do `.env` para o banco (login + user_loader); `.env` vira só semente do 1º admin
- [x] Tela `/usuarios` (admin): criar, redefinir senha, promover/rebaixar, remover
- [x] Tela `/conta` (todos): trocar a própria senha (confere senha atual)
- [x] Proteções anti-lockout: não remover/rebaixar o último admin nem a própria conta
- [x] Sidebar: "Usuários" (admin) + nome do usuário → "Minha conta"

---

## ✅ Suíte de Testes Automatizados (10/06/2026)

Rede de regressão (pytest) — fundação de qualidade antes da Fase H.

- [x] **49 testes** verdes: processing, migrations, auth, multiusuário, Minha conta
- [x] Banco isolado via `MATINE_DATA_DIR` (default `C:\MATINE` — produção inalterada); testes nunca tocam dados reais
- [x] `conftest.py` (fixtures app/client/db/users/login) + `pytest.ini` + `requirements-dev.txt`
- [x] Cobre: CSV multi-separador, conversão de valores BR, heurística de gênero, consolidação; runner de migrations (up/down da 007); guard de rotas e open-redirect; CRUD de usuários e proteções anti-lockout
- [x] README com seção Testes; rodar: `cd 06_APP && pip install -r requirements-dev.txt && pytest`

---

## ✅ Backup do Banco com Retenção (10/06/2026)

- [x] `backup_db.py` — cópia consistente via API do sqlite3 (funciona com WAL); retenção configurável (`--keep`, default 14)
- [x] Backups em `C:\MATINE\backups\` (respeita `MATINE_DATA_DIR`); agendável no Agendador de Tarefas
- [x] 3 testes (`tests/test_backup.py`): backup válido com schema, retenção, banco ausente → None
- [x] Validado contra o banco real (primeiro backup automático criado)

---

## 🔲 FASE H — Integrações (Sprint H-1 e H-2)

> Brainstorm realizado em 11/06/2026. Decisões registradas no MEMORY.md.

### Sprint H-1 — WhatsApp via Google Drive + Kommo *(próxima)*

**Fluxo definido:**
```
App gera planilha XLSX → sobe no Google Drive (pasta configurada) →
Kommo lê via Make ou integração nativa Google Sheets →
dispara WhatsApp pelo número conectado ao Kommo →
tipo de mensagem definido pela tag_crm
```

**Estrutura da planilha (a validar com o Kommo):**

| telefone | nome | tag_crm | empresa | categoria | vencimento | valor |
|----------|------|---------|---------|-----------|------------|-------|
| 5511... | João Silva | INADIMPLENTE_REGUA | INEPROTEC | Régua | 01/06/2026 | R$ 350,00 |

Tags mapeiam para templates no Kommo: `INADIMPLENTE_NOVO`, `INADIMPLENTE_REGUA`, `INADIMPLENTE_30DIAS`.

**Onda 1 — Fundação backend ✅ (15/06/2026):**
- [x] Migration `008_add_config_whatsapp` — tabela `config_whatsapp` por empresa
- [x] `gdrive.py` — módulo modular (Service Account + Shared Drive, `supportsAllDrives=True`): `testar_conexao`, `upload_xlsx` (cria/substitui), `disponivel`. Imports Google protegidos (app não quebra sem as libs); camada de auth isolada para OAuth na v2
- [x] `database.py` — `salvar_config_whatsapp` / `get_config_whatsapp` + credencial em `C:\MATINE\secrets\gdrive_{empresa}.json` (coluna guarda só o marcador `[file]`; JSON nunca em HTML)
- [x] `requirements.txt` — `google-api-python-client`, `google-auth`, `google-auth-httplib2`
- [x] `tests/test_whatsapp.py` — 12 testes (migration, config round-trip, gdrive create/replace). Suíte total: 64 verdes

**Onda 2 — UI + fluxo ✅ (15/06/2026):**
- [x] **Aba de Configuração WhatsApp** em Configurações + sublink na sidebar:
  - *Bloco Google Drive:* upload do JSON da SA (validado), ID da pasta no Shared Drive, template do nome do arquivo, botão Testar Conexão (AJAX → `gdrive.testar_conexao`)
  - *Bloco Kommo:* URL do webhook ou ID do pipeline
  - *Bloco Comportamento:* toggle de exportação automática (default OFF — geração **sob demanda**, decisão de 11/06)
- [x] **Rotas** `POST /whatsapp/configurar` (upload + validação JSON), `POST /whatsapp/testar` (AJAX → JSON), `POST /whatsapp/exportar`
- [x] Botão **"Exportar para WhatsApp"** em Envio de Mensagens — gera Planilha CRM + `gdrive.upload_xlsx` (aparece só quando o Drive está configurado)
- [x] Registro do envio na tabela `envios` (canal=`whatsapp_crm`, um por inadimplente)
- [x] Credencial nunca renderizada em HTML (AC) + **7 testes de rota**. Suíte total: **71 verdes**

**Falta para fechar a STORY-H-01 (próxima sessão):** onboarding real (criar Service Account + Shared Drive, testar conexão e exportação) e validação ponta a ponta com o Kommo → QA gate (InReview → Done).

### Sprint H-2 — Dashboard analítico *(entregue em código 17/06/2026)*

**Decisão de escopo (17/06):** o *Agendamento via Windows Task Scheduler* foi **removido** do H-2.
Pós-EPIC-02 o app roda no Render/Linux e não há ingestão automática do Synapta — não há o que
consolidar automaticamente. Os jobs de infra que importam (dump do Postgres p/ risco dos 90 dias +
keep-alive) ficam no backlog de infra (ver INSIGHTS → Infraestrutura).

- [x] **Dashboard analítico (STORY-H-02)** — rota `/dashboard` (login obrigatório, escopado pela
  empresa ativa) + link na sidebar. `db.dashboard_stats(empresa, dias=30)` agrega:
  - KPIs: total de inadimplentes, valor em aberto (R$), quitados, em renegociação, mensagens no período
  - Distribuição por categoria (Novos / Régua / Acima 30 dias) — qtd + valor
  - **Taxa de quitação pós-cobrança:** dos CPFs com `qtd_cobranca>0`, % hoje `QUITADO` (com numerador/denominador à vista)
  - **Evolução semanal** da carteira (bucketização ISO de `historico_atualizacoes`)
  - `dashboard.html` com gráficos **Chart.js** (linha + doughnut) + estado vazio amigável
  - Cross-dialect: datas pt-BR parseadas em Python (`_parse_dt_br`) — vale p/ SQLite e Postgres
  - Sem novas tabelas/deps de backend. **+11 testes** (`tests/test_dashboard.py`). Suíte: 102 passed, 1 skipped
- [ ] ~~Agendamento via Windows Task Scheduler~~ — **removido** (obsoleto pós-EPIC-02)
- [ ] Validação visual no app rodando (smoke) — próxima sessão
- [ ] *(v.next)* Taxa de resposta/conversões reais do WhatsApp — exige callback do Kommo

### Sprint H-3 — Canais de Comunicação + SMS *(scaffold entregue em código 17/06/2026)*

Reorganização de UX em Configurações: E-mail (Fase G) e WhatsApp (H-1) ficavam como abas
soltas. Agrupados sob "Canais de Comunicação" e somado o SMS como terceiro canal.

**Decisão de escopo (17/06):** a aba SMS é um **scaffold provider-agnostic** — a config e o
segredo já ficam prontos, mas a **camada de envio real** depende do provider (ainda TBD:
Twilio / Zenvia / Comtele). O agrupamento foi feito na **sidebar** (cabeçalho de grupo),
mantendo E-mail/WhatsApp/SMS como abas irmãs — preserva os deep-links `#tab-*` e os
redirects pós-save existentes (não foi necessário aninhar fisicamente as abas).

- [x] Submenu **"Canais de Comunicação"** na sidebar, agrupando os três canais (`layout.html`)
  - **Ajuste 18/06:** o grupo virou **colapsável** (toggle Bootstrap `#submenuCanais` + chevron, como o de Configurações) e **"Zona de Risco"** saiu de dentro do grupo — agora fica logo após "Clientes", antes dos canais
- [x] Nova aba **SMS** (STORY-H-03) — provider (select), remetente/Sender ID, chave de API, Account SID, endpoint, toggle ativo
- [x] Migration `011_add_config_sms` (cross-dialect) + `db.salvar_config_sms`/`get_config_sms`/`get_sms_api_key`/`tem_sms_api_key`
- [x] Chave de API **fora do banco**: `secrets/sms_{empresa}.key` (marcador `[file]`) + override por env `SMS_{empresa}_API_KEY` (Render). Nunca renderizada no HTML
- [x] Rotas `POST /sms/configurar` + `POST /sms/testar` (AJAX → JSON, valida sem chamar API) + **11 testes** (`tests/test_sms.py`). **Suíte SQLite: 116 passed, 1 skipped**
- [ ] **Envio SMS real** individual + em lote, com registro em `envios` (`canal='sms'`) — ⏸️ **adiado (Kommo-first, 18/06)**: não construir app-side enquanto o Kommo for o hub de disparo. Habilitar SMS um dia será via **Twilio dentro do Kommo** (zero código no app) ou Comtele direto do app (mais barato no BR). O scaffold já "deixa pronto" sem contratação
- [ ] Validação visual no app rodando (smoke) — próxima sessão

> Alinha com a visão SaaS: multi-canal (WhatsApp + E-mail + SMS) é funcionalidade universal, independente do segmento.
>
> **Decisão Kommo-first (18/06):** pesquisa confirmou que o Kommo **não tem SMS nativo** (só via
> gateway Twilio/RingCentral/Fromni; Comtele/Zenvia só via Make). Como o 1º projeto prioriza o
> **Kommo como hub de disparo**, o app fica como cérebro de dados (planilha + `tag_crm`) e o Kommo
> executa. Guia da plataforma: `docs/guides/kommo-plataforma.md`. Onboarding do fluxo real:
> `docs/guides/onboarding-h1-whatsapp-drive-kommo.md`.

---

## ✅ EPIC-02 — Cloud-Native / Stateless (ponte para a v2) *(concluído 16/06/2026 — no ar no Render)*

> Objetivo: disponibilizar o app por **URL** (Edilvo/Luana validam de qualquer máquina) tornando-o
> **stateless** — alicerce comum entre "rodar na nuvem" e a v2 SaaS. Mantém o modelo de **2 empresas**
> (multi-tenant real fica para o v2). Host **Render**, banco **PostgreSQL** gerenciado.
> Spec completa: `docs/stories/epic-02-cloud-native-stateless.md`. Esforço ~30h (~3–4 janelas).

**Por que stateless (e não só "SQLite num disco"):** resolve a preocupação de "não guardar
arquivos dos clientes no meu servidor" e remove os acoplamentos que quebram na nuvem — pickle de
estado (por-processo), arquivos em disco efêmero, keyring do Windows, `os.startfile` (derruba no Linux).

- [x] **Onda 0** — Deps (`psycopg[binary]`, `psycopg_pool`) + `DATABASE_URL`/`DIALECT` em `database.py`; import protegido; suíte 90 verdes ✅ 16/06
- [x] **Onda 1** — `_PGConn` wrapper (`?`→`%s`, commit/rollback, isolation_level); `get_conn()` ramifica SQLite↔Postgres; 4 COUNT aliases (`[0]`→`['cnt']`); runner `r['version']`/`row['max_ver']`; `_IntegrityError` cross-dialect; `_table_exists` guarda Postgres ✅ 16/06
- [x] **Onda 2** — `migrations/ddl.py` (`pk_int`, `blob`, `ts_default`); runner: sys.path + `ddl.ts_default()` em `ensure_migrations_table`; 001-004/007-010 com f-strings; 006 WAL guard sqlite; `database.py`: `INSERT OR IGNORE→ON CONFLICT DO NOTHING`, `lastrowid→RETURNING id`, 3× `datetime('now')→` param Python ✅ 16/06
- [x] **Onda 3** — Estado de sessão: pickle → tabela `estado_consolidacao` (BLOB/BYTEA) ✅ 15/06 — migration 009, `_salvar/_carregar/_limpar_estado` via blob no banco, `estado_existe`, +8 testes (suíte 79 verdes). Roda em SQLite hoje; pronta p/ Postgres
- [x] **Onda 4** — Stateless de arquivos ✅ 16/06 — migration 010 (`uploads_staging`: bytes do upload por empresa+tipo no banco); `/upload` grava no staging (não em disco), `/consolidar` e `/atualizar-base` leem em memória (`BytesIO` via `processing._ler_csv`); relatórios → **download ZIP** e Planilha CRM → **download xlsx** (geração em tmp, apagada após enviar); `os.startfile` e a rota `/abrir-relatorios` removidos; `_log` → stdout (arquivo só em modo local, via `EM_NUVEM`/`DATABASE_URL`). +13 testes (`test_uploads.py`). **Suíte: 90 verdes.** Roda em SQLite hoje; staging pronto p/ Postgres (BLOB→BYTEA)
  - **Decisão:** `/atualizar-base` deixou de gravar os TXT/XLSX de "novos/saídos" em disco (eram artefato do "abrir pasta"). A informação segue nos contadores do flash e na tela Base por categoria. Reexportar esses recortes como download é candidato de v.next se houver demanda
- [x] **Onda 5** — Segredos → env vars + Secret File do Drive; blindar keyring ✅ 16/06 — `_env_get` prioriza `os.environ` (Render/CI); keyring ignorado quando `DIALECT='postgres'` (SMTP vem de `SMTP_{empresa}_SENHA`); `get_gdrive_credentials_path` lê `GOOGLE_SA_{empresa}_JSON_PATH` (Secret File do Render). **Suíte: 90 verdes.**
- [x] **Onda 6** — Testes dual-dialect ✅ 16/06 — conftest parametrizado (`TEST_DIALECT=postgres` sobe Postgres efêmero via testcontainers); `_tabelas()` cross-dialect (3 arquivos); `r['version']/['cnt']/['coluna']` no lugar de `r[0]`; 7 testes `sqlite_only`. Suíte SQLite: 90 verdes.
- [x] **Onda 7** — Deploy Render ✅ 16/06 — **app no ar** (Helder confirmou acesso pela URL em 17/06). `render.yaml` (Web Service `matine-cobranca` gunicorn `-w 2`, `rootDir=06_APP`) + Postgres gerenciado `matine-db`; env vars `DATABASE_URL`/`FLASK_SECRET_KEY`/`MATINE_DATA_DIR=/tmp/matine`/`APP_USUARIO`/`APP_SENHA`/`SMTP_*_SENHA`; `06_APP/Procfile`. Postgres na nuvem valida o dual-dialect na prática.
  - **Pós-deploy:** smoke test HTTP ✅ (18/06 — guard de auth OK, rotas 302/200, sem 500, Postgres conectado). Falta a parte interativa (fluxo logado) + **trocar senha admin default**.
- [x] **Hardening — migrations concorrentes** ✅ 17/06 — com `gunicorn -w 2` os 2 workers aplicavam migrations em paralelo no boot (falha de PK em `schema_migrations`). `runner.apply_pending` agora serializa via `pg_advisory_lock` de sessão (Postgres; no-op em SQLite) em try/finally. +2 testes. Suíte: 91 passed, 1 skipped. Essencial agora que haverá mudanças de banco frequentes.

> Reaproveita 100% no v2: o banco já em Postgres e o app já stateless são pré-requisitos diretos
> da visão SaaS multi-tenant abaixo. Falta, depois, generalizar "2 empresas" → "N tenants".

---

## 💡 INSIGHTS — Próxima Versão

Observações e aprendizados do uso real. Serão tratados após Fase H como backlog da v2.

### Operação

- **Separação automática Quitado × Renegociado:** Hoje é revisão manual (coluna `Situacao` em branco no XLSX). A distinção automática exige rastrear se o CPF saiu dos vencidos e apareceu no À Vencer — o arquivo Synapta mistura os dois casos. Solução robusta requer lógica de estado por CPF com janela temporal.

- **Alunos sem telefone:** ~252 alunos sem telefone na base. O aviso de "sem cadastro" existe, mas não há fluxo para enriquecer o cadastro dentro do app. Considerar tela de enriquecimento manual ou integração com Synapta.

- **Heurística de gênero frágil:** Nomes terminados em "a" → sra. Falha em nomes como "Joshua", "Elias", "Matias". Melhorar com lista de exceções ou biblioteca de classificação de nomes.

- **Régua inteligente por comportamento:** Hoje a régua é rígida por dias de atraso. Evoluir para: aluno que quitou na 1ª mensagem → régua mais suave; aluno que nunca responde → escalar canal ou marcar para negativação; renegociado → pausar cobranças automáticas.

### Documentação

- **Central de Ajuda — incluir prints das telas:** o conteúdo passo a passo já existe, mas falta ilustrar cada seção com screenshots das telas reais para a operadora se localizar visualmente. Revisar também o texto (Edilvo/Helder fariam um passe de revisão). *(observação de 10/06, a fazer quando houver disponibilidade)*

### Produto

- **Dashboard analítico:** Qtd e valor de inadimplentes por período, evolução de quitações, taxa de resposta ao WhatsApp. Hoje não existe nenhuma visão histórica no app.

- **Régua configurável por aluno:** Hoje a régua é por categoria (dias de atraso). Ideal seria configurar frequência por aluno (ex.: cliente preferencial com régua mais suave).

- **Negativação automática:** Estava no plano original. Clientes acima de 30 dias sem resposta entrariam em fluxo de negativação. Requer conformidade legal e parceiro de negativação (Serasa, SPC).

- **Multi-usuário — permissões granulares:** A base multi-usuário já existe (tabela `usuarios`, perfis admin/operador). Evolução futura: usuários **por empresa** e permissões mais finas por função (ex.: operador que só envia, não configura).

- **Relatório gerencial semanal:** PDF/Excel gerado automaticamente ao final da semana para o gestor — inadimplentes totais, cobrados, quitados, evolução da carteira.

- **PWA / acesso mobile:** transformar o app em Progressive Web App — o gestor acompanha pelo celular sem instalar nada. Custo praticamente zero (manifest.json + service worker).

### Técnico

- **Arquivo Synapta sem CPF:** Quando o arquivo À Vencer não tem CPF, o cruzamento é feito por nome (match aproximado). Erros de grafia resultam em CPF vazio e o aluno não é reconhecido como "Em Renegociação". Solução: solicitar ao Synapta exportação com CPF ou implementar fuzzy matching.

- **Pickle de sessão sem expiração:** O estado de consolidação fica em pickle indefinidamente. Se o arquivo fonte mudar sem nova consolidação, os dados exibidos ficam desatualizados silenciosamente. Considerar timestamp de validade ou aviso visual de sessão antiga.

- **Relatórios acumulam sem limpeza:** A pasta `C:\MATINE\relatorios\` cresce indefinidamente. Implementar política de retenção (ex.: 90 dias) ou tela de gerenciamento.

### Infraestrutura (nuvem / Render) *(EPIC-02, no ar desde 16/06/2026)*

- **🔴 Postgres free do Render expira em ~90 dias:** o banco gerenciado `matine-db` no plano free é **deletado após ~90 dias** (Render avisa por e-mail antes). É o **único risco real de perda de dados** (merge/redeploy NÃO apagam o banco — código e dados são serviços separados). Antes de virar produção pro Edilvo: migrar para Postgres **pago** (ou outro provedor) e definir **estratégia de backup** (dump periódico automatizado). *(observado 17/06/2026)*

- **Cold start do free tier (~30–60s):** o Web Service `matine-cobranca` hiberna após ~15 min de inatividade; o primeiro acesso depois disso leva ~30–60s (vimos o 503 inicial no smoke test). Para Edilvo/Luana = "a primeira tela demora, depois fica rápida". Mitigações: upgrade do plano (sem hibernação) ou keep-alive (ping periódico externo). *(observado 17/06/2026)*

---

## 🔭 VISÃO v2 — Produto SaaS Multi-Tenant *(discussão estratégica — 11/06/2026)*

> Decisão: o produto evoluirá de solução local das escolas do Edilvo para **plataforma SaaS de cobrança de inadimplentes**, multi-tenant, cloud-native.
> Edilvo = cliente zero (laboratório sem cobrança) — cada decisão nas escolas dele deve ser generalizável.

### Decisões arquiteturais a tomar antes de escalar

| Decisão | Situação atual | Alvo v2 | Impacto |
|---------|---------------|---------|---------|
| Banco | SQLite local | PostgreSQL cloud | Multi-tenant real |
| Storage | `C:\MATINE\` Windows | S3 ou similar por tenant | Portabilidade |
| Deploy | Flask local Windows | Cloud (Railway / Render / AWS) | Acessibilidade |
| Credenciais | Keyring Windows | Vault cloud (HashiCorp ou similar) | Segurança multi-tenant |
| Empresas | 2 hardcoded | N tenants configuráveis | Modelo de dados |
| Fonte de dados | Synapta CSV | Importação genérica com mapeamento de colunas | Universalidade |
| WhatsApp | Kommo + Drive | Provider configurável por tenant | Flexibilidade |

### Funcionalidades universais (independem do segmento)

- Importação de inadimplentes via CSV/XLSX com mapeamento de colunas configurável
- Régua de cobrança configurável (dias, canais, frequência)
- Multi-canal: WhatsApp + E-mail + (futuro) SMS
- Dashboard analítico por tenant
- Gestão de usuários com perfis por empresa
- Relatório gerencial exportável
- Negativação automática (parceiro TBD)

### O que é específico das escolas (não generalizar)

- Nomenclatura "aluno" → generalizar para "devedor" ou "cliente"
- Lógica de gênero (sr./sra.) → opcional/configurável
- Templates educacionais → apenas exemplos padrão, não hardcoded
- Integração Synapta → descontinuar quando o sistema for substituído
