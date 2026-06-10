# STORY-01-05: Schema Migrations + Indices + WAL Mode
**Epic:** EPIC-01 Sprint Zero
**Status:** Done
**Esforco estimado:** ~12h
**Prioridade:** P1
**Debitos resolvidos:** DB-A01, ARCH-02, DB-A02, DB-A03, DB-B01, DB-C02 (parcial)

---

## Contexto

O maior bloqueador tecnico para a Fase H. O `init_db()` atual tem 163 linhas com 7 fases de migracao misturadas e sem como saber qual versao do schema esta em producao. Qualquer falha durante uma migracao pode corromper o banco sem como voltar atras. Este story implementa a fundacao de versionamento que todas as migracoes futuras usarao.

---

## Acceptance Criteria

### AC-01 — Tabela `schema_migrations` criada
- [x] Nova tabela no SQLite:
  ```sql
  CREATE TABLE IF NOT EXISTS schema_migrations (
    version    INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
  );
  ```
- [x] Criada pelo `init_db()` ANTES de qualquer outra operacao de schema (`runner.ensure_migrations_table`)

### AC-02 — Refatorar `init_db()` em scripts atomicos numerados
- [x] Diretorio `06_APP/migrations/` criado com scripts Python numerados
- [x] Cada script contem: `version`, `name`, `up(conn)` e `down(conn)`
- [x] Scripts existentes numerados a partir do historico atual:
  - `001_initial_schema.py` — schema base (inadimplentes, templates)
  - `002_add_historico.py` — tabela historico_atualizacoes
  - `003_add_envios.py` — tabela envios
  - `004_add_config_email.py` — tabela config_email
  - `005_add_indices.py` — indices de performance (DB-A02, DB-A03)
  - `006_enable_wal.py` — WAL mode (DB-B01); FK pragma fica no `get_conn()` (por-conexao)
- [x] `init_db()` refatorado para: (1) criar schema_migrations, (2) verificar versao atual, (3) aplicar apenas scripts pendentes em ordem (via `migrations/runner.py`)

### AC-03 — Idempotencia garantida
- [x] Executar `init_db()` multiplas vezes nao duplica tabelas nem falha (testado 2x)
- [x] Script que ja foi aplicado e ignorado (verificacao via `schema_migrations.version`)
- [x] Banco existente sem `schema_migrations` e reconhecido como "versao legada" e 001-004 sao marcados como aplicados sem re-executar (`_BASELINE_LEGADO` + `_table_exists`)

### AC-04 — Indices de performance adicionados (DB-A02, DB-A03)
- [x] `CREATE INDEX IF NOT EXISTS idx_inadimplentes_empresa ON inadimplentes(empresa)`
- [x] `CREATE INDEX IF NOT EXISTS idx_templates_empresa ON templates(empresa)`
- [x] `CREATE INDEX IF NOT EXISTS idx_envios_empresa_data ON envios(empresa, data_envio)`
- [x] `CREATE INDEX IF NOT EXISTS idx_historico_empresa ON historico_atualizacoes(empresa)`
- [x] `CREATE INDEX IF NOT EXISTS idx_config_email_empresa ON config_email(empresa)`
- [x] Indices criados via migration 005, nao em `init_db()` diretamente

### AC-05 — WAL mode e FK pragma ativados (DB-B01, parte de DB-C02)
- [x] `get_conn()` em `database.py` habilita:
  ```python
  conn.execute("PRAGMA journal_mode=WAL")
  conn.execute("PRAGMA foreign_keys=ON")
  ```
- [x] WAL mode permite leituras concorrentes durante escritas (necessario para Fase H) — confirmado `journal_mode=wal` no banco real
- [x] FK ON prepara o banco para receber constraints formais nas migrations seguintes

### AC-06 — Sem regressoes na operacao atual
- [x] App sobe e rotas `/`, `/resultado`, `/base`, `/configuracoes` retornam 200 apos a refatoracao
- [x] `salvar_base()` / fluxo de base preservado (schema final identico ao anterior)
- [x] `registrar_envio()` funciona normalmente (testado)
- [x] Banco existente em `C:\MATINE\banco\inadimplencia.db` migrado sem perda de dados (1024 inadimplentes + 10 templates preservados; backup `inadimplencia_backup_*.db` criado antes)

---

## Arquivos a Modificar / Criar

- `06_APP/database.py` — refatorar `init_db()` + atualizar `get_conn()`
- `06_APP/migrations/` — novo diretorio com 006 scripts
- `06_APP/migrations/__init__.py` — vazio (torna o diretorio um modulo Python)
- `06_APP/migrations/runner.py` — logica de aplicar scripts pendentes

---

## Ordem de Execucao no Deploy

1. Backup manual do `inadimplencia.db` antes de rodar
2. Iniciar o servidor (init_db detecta banco existente, aplica migrations pendentes)
3. Verificar log: "6 migrations aplicadas com sucesso"
4. Testar fluxo completo

---

## Testes Esperados

- [x] Banco novo (ambiente de desenvolvimento): todas as 6 migrations aplicadas, tabela schema_migrations com 6 registros, 5 indices, WAL, 8 templates padrao
- [x] Banco existente (producao): migrations 005 e 006 aplicadas (001-004 marcadas como ja aplicadas) — confirmado no banco real (1024 registros preservados)
- [x] Executar servidor duas vezes: segunda execucao nao re-aplica nenhuma migration
- [x] Verificacao programatica: indices criados, schema_migrations populada (1..6), WAL mode ativo

---

## File List

- `06_APP/migrations/__init__.py` — torna o diretorio um pacote
- `06_APP/migrations/runner.py` — descoberta + aplicacao atomica de migrations pendentes
- `06_APP/migrations/001_initial_schema.py` — inadimplentes + templates (forma final)
- `06_APP/migrations/002_add_historico.py` — historico_atualizacoes
- `06_APP/migrations/003_add_envios.py` — envios
- `06_APP/migrations/004_add_config_email.py` — config_email
- `06_APP/migrations/005_add_indices.py` — 5 indices de performance
- `06_APP/migrations/006_enable_wal.py` — WAL (non-transactional)
- `06_APP/database.py` — `get_conn()` (WAL+FK), `init_db()` refatorado, `_table_exists`, `_seed_templates_padrao`, carga do runner por caminho

## Dev Notes

- **Por que carregar migrations por caminho (importlib):** nomes de arquivo comecam com
  digito (`001_...`), invalidos como modulo Python para `import`. O runner usa
  `spec_from_file_location` para carregar por caminho; idem `database.py` carrega o runner.
  Funciona de qualquer cwd.
- **Atomicidade vs `executescript`:** o runner usa `conn.isolation_level = None` (autocommit)
  e controla BEGIN/COMMIT manualmente por migration. Migrations usam um `conn.execute()` por
  statement — `executescript` forca um COMMIT implicito e quebraria a transacao da migration.
- **WAL fora de transacao:** `PRAGMA journal_mode=WAL` nao roda dentro de transacao; a
  migration 006 tem `transactional = False`. `get_conn()` tambem seta WAL+FK por conexao
  (WAL e persistente; FK e por-conexao).
- **Schema final direto:** as migrations 001-004 criam o schema FINAL (sem replay da cadeia
  de ALTERs das Fases C/D/E). Num banco legado elas sao marcadas como aplicadas; num banco
  novo, criadas. Resultado identico ao schema produzido pelo `init_db()` antigo.
- **Normalizacao legada removida:** os UPDATEs de categorias 'A'/'B' e preenchimento de
  `dias_de/dias_ate` (Fases C/F) sairam do `init_db()` — producao ja os aplicou via boots
  anteriores; bancos novos nunca tem esses dados legados.
- **Seeding de templates** permanece idempotente no `init_db()` (pos-migrations), preservando
  o comportamento atual de garantir os 4 templates padrao por empresa.
- **Validacao:** `py_compile` OK; suite de teste temporaria (novo/idempotente/legado/regressao)
  100% PASS; app real subiu e migrou o banco de producao (legado) sem perda de dados.

## Change Log

| Data | Status | Autor | Nota |
|------|--------|-------|------|
| (origem) | Draft | @sm | Story criada |
| 10/06/2026 | Draft -> Done | @dev | Sistema de migrations versionadas (schema_migrations + runner + 6 scripts), WAL+FK em get_conn, deteccao de banco legado. Testado em banco novo, idempotencia, legado e banco real (1024 registros preservados, backup criado) |

---

*STORY-01-05 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
