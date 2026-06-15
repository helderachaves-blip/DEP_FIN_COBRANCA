# EPIC-02 — Cloud-Native / Stateless (ponte para a v2)

> Status: **Planejado** (decisão estratégica 15/06/2026). Implementação inicia na próxima janela.
> Tipo: especificação técnica (não é arquivo de gestão). Gestão em `PLANO_DE_ACAO.md` / `ROADMAP.md`.

---

## Contexto

Hoje o app (`06_APP/`, Flask + pandas) roda **só na máquina local Windows**: SQLite em
`C:\MATINE`, estado de sessão em **pickle no disco**, uploads/relatórios em disco, segredos no
**keyring do Windows** e no `.env`, e abre o Explorer com `os.startfile`. Para o Edilvo e a Luana
validarem por uma **URL** (de qualquer máquina), o app precisa rodar num host Linux na nuvem.

Decidiu-se ir além do mínimo e tornar o app **stateless**, porque esse é o **alicerce comum**
entre "rodar na nuvem" e a futura **v2 SaaS** — e porque resolve a preocupação de "não quero
guardar os arquivos dos clientes ocupando meu servidor" (app stateless = não guarda arquivo nenhum).

### Decisões tomadas (15/06/2026)
- **Caminho B — Stateless** (mantém o modelo de **2 empresas**; não é o multi-tenant completo).
- Host: **Render** (Vercel descartada — serverless não serve a Flask/pandas com estado).
- Banco: **PostgreSQL gerenciado** (Render Postgres).
- **1 deploy / poucos workers** por ora (multi-instância passa a ser possível, mas não é meta).

### Esclarecimentos de produto
- "Acessível por várias máquinas" = **uma URL pública**; **1 instância** atende Edilvo + Luana.
  Não confundir com "várias instâncias" (escala/redundância — fica para o v2).
- "Arquivos na máquina do cliente" **não é possível** num app web (sandbox do browser). A solução
  equivalente é o app **stateless**: processa upload em memória, grava só o resultado no Postgres,
  entrega relatórios via download. Nada de arquivo retido no servidor.

---

## Decisões de arquitetura

1. **Banco — psycopg3 + camada fina, dual-dialect.** SQLite em dev/testes; Postgres quando
   `DATABASE_URL` existe. Wrapper conn/cursor unifica a API (mantém as ~96 queries quase intactas).
   `get_conn()` ramifica: SQLite como hoje; Postgres via `psycopg_pool.ConnectionPool` +
   `row_factory=dict_row`. Descartado SQLAlchemy (reescreveria ~96 queries). Rollback trivial.
2. **Estado de sessão — pickle → blob no Postgres.** Tabela `estado_consolidacao(empresa PK,
   payload BYTEA, atualizado_em)`. Reaproveita o mesmo `pickle.dumps` do dict atual (zero perda de
   dtype). `_salvar/_carregar/_limpar_estado` (`app.py:259-311`) passam a usar a tabela.
3. **Arquivos — stateless.** Upload processado em memória (`processing._ler_csv:48-69` passa a ler
   do stream); resultado só no Postgres; arquivo bruto descartado. Relatórios/Planilha CRM gerados
   sob demanda e entregues como **download (ZIP)**. **Remover `os.startfile`** (`app.py:945,1372`).
   Object storage não é necessário neste escopo.
4. **Segredos — env vars + Secret File do Render.** `_env_get` (`app.py:69-96`) prioriza
   `os.environ` (sem isso a secret_key regenera a cada deploy e desloga todos). SMTP via env
   `SMTP_<EMPRESA>_SENHA` (fallback já existe em `database.py:55-74`); blindar `keyring.set_password`.
   Google Drive SA JSON via **Secret File** (o código já lê de path — `gdrive.py:49-62`).
5. **Logs — stdout** (o Render captura). Arquivo só em modo local.
6. **Backup — `pg_dump`/gerenciado** quando Postgres; SQLite como hoje (`backup_db.py`).

---

## Ondas de execução (incrementais, cada uma testável)

| Onda | Objetivo | Arquivos principais | Esforço |
|------|----------|---------------------|---------|
| **0** | Deps + switch de dialeto (`DATABASE_URL`/`DIALECT`) sem usar ainda; `psycopg[binary]`, `psycopg_pool` | `requirements.txt`, `database.py` | ~0,5h |
| **1** | Wrapper conn/cursor; `get_conn()` ramifica + pool PG; helper `?`→`%s`; acessos posicionais `[0]`→alias (`database.py:484,521,706,793`; `runner.py:37,42`) | `database.py`, `migrations/runner.py` | ~5h |
| **2** | Migrations cross-dialect: novo `ddl.py` (PK auto-increment, `now_default`, `table_exists`); editar 001–004/007/008; guarda WAL na 006; `INSERT OR IGNORE`→`ON CONFLICT` (`database.py:287`); `datetime('now')`→`CURRENT_TIMESTAMP` (655,664); `lastrowid`→`RETURNING` (338) | `migrations/*`, `database.py` | ~5h |
| **3** | **Matar o pickle**: migration `009_estado_consolidacao`; reescrever estado para blob no Postgres; revisar os ~8 pontos que usam estado | `app.py`, `database.py`, `migrations/009_*` | ~5h |
| **4** | **Stateless de arquivos**: upload em memória; relatórios/CRM via download (ZIP); remover `os.startfile`; logs→stdout | `app.py`, `processing.py` | ~6h |
| **5** | Segredos→env: `_env_get` prioriza `os.environ`; blindar keyring; Drive via Secret File | `app.py`, `database.py`, `gdrive.py` | ~2h |
| **6** | Testes dual-dialect: conftest parametrizado; ajustar `PRAGMA table_info`/`sqlite_master` (`test_migrations.py`, `test_whatsapp.py`); Postgres efêmero (testcontainers ou serviço de CI) | `conftest.py`, `tests/*`, `pytest.ini` | ~4h |
| **7** | **Deploy Render**: Web Service (branch `homologacao`), `Procfile` (gunicorn), Render Postgres, env vars, Secret File do Drive, `runtime.txt`; smoke test ponta a ponta; trocar senha admin | `Procfile`, `runtime.txt` (raiz do repo) | ~3h |

**Esforço total estimado: ~30h (~3–4 janelas de 5h).**

---

## Verificação (end-to-end)
1. **Local SQLite (regressão):** `cd 06_APP && pytest` → os ~91 testes verdes sem `DATABASE_URL`.
2. **Local Postgres:** Postgres efêmero (testcontainers/Docker), `DATABASE_URL=...`, `pytest` contra PG.
3. **Stateless manual:** 2 workers gunicorn local; consolidar e abrir `/resultado` (lê do Postgres,
   não de pickle); confirmar que nenhum `.pkl` é criado.
4. **Render:** deploy da `homologacao` → importar CSV (base vazia), consolidar, baixar relatório (ZIP),
   testar SMTP (env) e exportação WhatsApp (Drive via Secret File); trocar a senha do admin default.
5. Confirmar nos logs do Render que `_log` sai em stdout e que nenhum caminho `C:\` é tocado.

---

## Fora de escopo (próximos rounds / v2)
- Multi-tenant real (N clientes, isolamento por tenant, usuários por empresa, RBAC).
- Object storage (S3/R2) para histórico de relatórios; Redis; autoscaling; multi-região.
- Conversão de tipos TEXT→DATE e INTEGER→BOOLEAN (churn sem ganho imediato).
- Persistir senha SMTP pela UI na nuvem (hoje via env; futuro: coluna cifrada).

---

## Mapeamento de portabilidade (referência da investigação 15/06/2026)
- **SQLite-específico:** 62 placeholders `?`; 6 PKs `AUTOINCREMENT`; `INSERT OR IGNORE` (1);
  `datetime('now')` (5); `PRAGMA` (WAL/foreign_keys/table_info); `sqlite_master`; `lastrowid`;
  migration 006 (WAL) vira no-op no PG.
- **Acoplamentos com a máquina local:** pickle de estado (`estado_*.pkl`), uploads/relatórios/
  crm-exports em disco, keyring (SMTP), SA JSON em `secrets/`, secret_key no `.env`, `os.startfile`,
  logs em arquivo.
- **Multi-tenancy atual:** `EMPRESAS = ('INEPROTEC','MATRICULAEAD')` hardcoded (`database.py:19`);
  usuários **globais** (sem coluna empresa); dados/config scoped por coluna `empresa`. Generalizar
  para N tenants é v2 (fora deste épico).
