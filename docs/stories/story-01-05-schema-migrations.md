# STORY-01-05: Schema Migrations + Indices + WAL Mode
**Epic:** EPIC-01 Sprint Zero
**Status:** Draft
**Esforco estimado:** ~12h
**Prioridade:** P1
**Debitos resolvidos:** DB-A01, ARCH-02, DB-A02, DB-A03, DB-B01, DB-C02 (parcial)

---

## Contexto

O maior bloqueador tecnico para a Fase H. O `init_db()` atual tem 163 linhas com 7 fases de migracao misturadas e sem como saber qual versao do schema esta em producao. Qualquer falha durante uma migracao pode corromper o banco sem como voltar atras. Este story implementa a fundacao de versionamento que todas as migracoes futuras usarao.

---

## Acceptance Criteria

### AC-01 — Tabela `schema_migrations` criada
- [ ] Nova tabela no SQLite:
  ```sql
  CREATE TABLE IF NOT EXISTS schema_migrations (
    version    INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
  );
  ```
- [ ] Criada pelo `init_db()` ANTES de qualquer outra operacao de schema

### AC-02 — Refatorar `init_db()` em scripts atomicos numerados
- [ ] Diretorio `06_APP/migrations/` criado com scripts Python numerados
- [ ] Cada script contem: `version`, `name`, `up(conn)` e `down(conn)`
- [ ] Scripts existentes numerados a partir do historico atual:
  - `001_initial_schema.py` — schema base (inadimplentes, templates)
  - `002_add_historico.py` — tabela historico_atualizacoes
  - `003_add_envios.py` — tabela envios
  - `004_add_config_email.py` — tabela config_email
  - `005_add_indices.py` — indices de performance (DB-A02, DB-A03)
  - `006_enable_wal.py` — WAL mode + FK pragma (DB-B01)
- [ ] `init_db()` refatorado para: (1) criar schema_migrations, (2) verificar versao atual, (3) aplicar apenas scripts pendentes em ordem

### AC-03 — Idempotencia garantida
- [ ] Executar `init_db()` multiplas vezes nao duplica tabelas nem falha
- [ ] Script que ja foi aplicado e ignorado (verificacao via `schema_migrations.version`)
- [ ] Banco existente sem `schema_migrations` e reconhecido como "versao legada" e os scripts de criacao inicial sao marcados como aplicados sem re-executar

### AC-04 — Indices de performance adicionados (DB-A02, DB-A03)
- [ ] `CREATE INDEX IF NOT EXISTS idx_inadimplentes_empresa ON inadimplentes(empresa)`
- [ ] `CREATE INDEX IF NOT EXISTS idx_templates_empresa ON templates(empresa)`
- [ ] `CREATE INDEX IF NOT EXISTS idx_envios_empresa_data ON envios(empresa, data_envio)`
- [ ] `CREATE INDEX IF NOT EXISTS idx_historico_empresa ON historico_atualizacoes(empresa)`
- [ ] `CREATE INDEX IF NOT EXISTS idx_config_email_empresa ON config_email(empresa)`
- [ ] Indices criados via migration 005, nao em `init_db()` diretamente

### AC-05 — WAL mode e FK pragma ativados (DB-B01, parte de DB-C02)
- [ ] `get_conn()` em `database.py` habilita:
  ```python
  conn.execute("PRAGMA journal_mode=WAL")
  conn.execute("PRAGMA foreign_keys=ON")
  ```
- [ ] WAL mode permite leituras concorrentes durante escritas (necessario para Fase H)
- [ ] FK ON prepara o banco para receber constraints formais nas migrations seguintes

### AC-06 — Sem regressoes na operacao atual
- [ ] `consolidar()` funciona normalmente apos a refatoracao
- [ ] `salvar_base()` funciona normalmente
- [ ] `registrar_envio()` funciona normalmente
- [ ] Banco existente em `C:\MATINE\banco\inadimplencia.db` e migrado sem perda de dados

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

- [ ] Banco novo (ambiente de desenvolvimento): todas as 6 migrations aplicadas, tabela schema_migrations com 6 registros
- [ ] Banco existente (producao): migrations 005 e 006 aplicadas (001-004 marcadas como ja aplicadas)
- [ ] Executar servidor duas vezes: segunda execucao nao re-aplica nenhuma migration
- [ ] Verificar com DB Browser: indices criados, schema_migrations populada, WAL mode ativo

---

*STORY-01-05 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
