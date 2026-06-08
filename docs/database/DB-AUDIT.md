# Database Audit — MAT-INE Inadimplencia 2026

**Auditado por:** Dara (@data-engineer)
**Data:** 2026-06-04
**Fonte analisada:** `06_APP/database.py`
**Engine:** SQLite 3
**Banco:** `C:\MATINE\banco\inadimplencia.db`

---

## Sumario Executivo

| Severidade | Quantidade | Status |
|-----------|-----------|--------|
| CRITICO   | 2         | Aberto |
| ALTO      | 4         | Aberto |
| MEDIO     | 5         | Aberto |
| BAIXO     | 3         | Aberto |
| **Total** | **14**    |        |

---

## Debitos Criticos

### DB-C01 — Senha SMTP armazenada em texto plano

**Tabela:** `config_email`
**Coluna:** `smtp_senha`
**Arquivo:** `database.py` ln 362-368 (`salvar_config_email`)
**Arquivo:** `database.py` ln 373-376 (`get_config_email`)

A funcao `salvar_config_email` recebe a senha como parametro `str` e a persiste diretamente na coluna `smtp_senha TEXT` sem qualquer forma de criptografia ou hashing. A funcao `get_config_email` retorna o dicionario completo com a senha em texto plano para qualquer caller.

**Risco:** Qualquer acesso ao arquivo .db (backup, copia indevida, acesso ao sistema de arquivos) expoe credenciais SMTP diretamente. Se o servidor de e-mail usar autenticacao OAuth2 ou credenciais de conta Google/Microsoft, o comprometimento e irreversivel sem rotacao de senha.

**Correcao recomendada:**
- Usar `cryptography.fernet` para criptografar o valor antes de persistir
- Armazenar a chave de criptografia em variavel de ambiente ou arquivo separado fora do banco
- Alternativa minima: usar Python `keyring` para armazenamento seguro de credenciais no SO

---

### DB-C02 — Ausencia total de foreign key constraints

**Arquivo:** `database.py` ln 139-163 (`init_db` — bloco executescript inicial)

O SQLite tem suporte a foreign keys, mas estas precisam ser habilitadas explicitamente com `PRAGMA foreign_keys = ON` a cada conexao. Nenhuma das cinco tabelas declara FOREIGN KEY, e o pragma nao e ativado em `get_conn()` (ln 121-124).

**Impacto concreto:**
- Registros em `envios` podem referenciar CPFs inexistentes em `inadimplentes` (dados orfaos)
- Registros em `envios` podem referenciar titulos de templates deletados
- `limpar_base()` (ln 315-319) deleta inadimplentes sem propagar para `envios` — historico de envios fica orfao
- Nao existe cascading delete em nenhuma relacao

**Correcao recomendada:**
- Adicionar `PRAGMA foreign_keys = ON` em `get_conn()`
- Declarar FOREIGN KEY em `envios.cpf+empresa` -> `inadimplentes(cpf, empresa)` com ON DELETE SET NULL
- Declarar FOREIGN KEY em `envios.template_titulo` -> `templates(titulo)` com ON DELETE SET NULL

---

## Debitos Altos

### DB-A01 — Schema sem versionamento formal (migracoes inline)

**Arquivo:** `database.py` ln 133-261 (funcao `init_db` completa)

Todo o schema e suas 6+ fases de evolucao estao embutidas em uma unica funcao `init_db()` com ALTER TABLE condicionais que verificam a existencia de colunas via PRAGMA. Esta abordagem tem varios problemas:

- **Nao e idempotente de forma garantida:** Se uma migracao falhar no meio, o schema fica em estado inconsistente sem rollback
- **Nao ha registro de qual versao o banco esta:** Nao existe tabela `schema_version` ou equivalente
- **Impossivel fazer rollback:** Nao ha DOWN migration para nenhuma fase
- **Risco em producao:** A funcao `init_db()` e chamada na inicializacao do app — um erro de migracao derruba o servico

**Evidencias de evolucao ad-hoc:** Fases A, B, C, D, E, F, G identificadas apenas por comentarios inline.

**Correcao recomendada:**
- Criar tabela `schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT)`
- Separar cada fase em funcao de migracao numerada: `migrate_001_fase_c()`, etc.
- Executar migracoes em transacao com rollback em caso de erro
- Alternativa: adotar Alembic (mesmo para SQLite)

---

### DB-A02 — Query get_envios_hoje usa LIKE em campo TEXT de data

**Arquivo:** `database.py` ln 335-349 (`get_envios_hoje`)

```python
rows = conn.execute(
    "SELECT * FROM envios WHERE empresa=? AND data_envio LIKE ?",
    (empresa, f"{hoje}%")
).fetchall()
```

A coluna `data_envio` e TEXT no formato `DD/MM/YYYY HH:MM:SS`. O filtro usa `LIKE '04/06/2026%'` em full scan da tabela — sem indice, o SQLite percorre todos os registros de `envios`. Com crescimento do historico de envios (centenas por dia * meses de operacao), esta query se torna O(n).

**Agravante:** A funcao e chamada frequentemente pois controla o throttle diario de disparos.

**Correcao recomendada:**
- Criar indice: `CREATE INDEX idx_envios_empresa_data ON envios(empresa, data_envio)`
- Ou converter `data_envio` para formato ISO 8601 (YYYY-MM-DD HH:MM:SS) para permitir range queries: `WHERE data_envio >= '2026-06-04' AND data_envio < '2026-06-05'`

---

### DB-A03 — Ausencia de indices em coluna empresa (todas as tabelas)

**Arquivo:** `database.py` — ausencia em todo o arquivo

Praticamente todas as queries da aplicacao incluem `WHERE empresa = ?` como filtro principal:
- `carregar_base` (ln 285): `WHERE empresa = ?`
- `salvar_base` (ln 292): `WHERE empresa = ?`
- `get_templates` (ln 267): `WHERE empresa = ? AND ativo = 1`
- `status_base` (ln 319): `WHERE empresa = ?`
- `get_envios_hoje` (ln 335): `WHERE empresa = ? AND ...`

Nenhum desses filtros tem suporte de indice. Com dois tenants ativos (INEPROTEC e MATRICULAEAD), o SQLite descarta ~50% dos registros via full scan a cada query.

**Correcao recomendada:**
```sql
CREATE INDEX idx_inadimplentes_empresa ON inadimplentes(empresa);
CREATE INDEX idx_templates_empresa_ativo ON templates(empresa, ativo);
CREATE INDEX idx_envios_empresa_data ON envios(empresa, data_envio);
CREATE INDEX idx_historico_empresa ON historico_atualizacoes(empresa);
```

---

### DB-A04 — salvar_base nao usa transacao atomica (risco de inconsistencia)

**Arquivo:** `database.py` ln 292-343 (`salvar_base`)

A funcao `salvar_base` realiza uma operacao critica: DELETE de saidos + UPSERT de todos os atuais + INSERT em `historico_atualizacoes`. O bloco usa `with get_conn() as conn:` que no sqlite3 do Python e um context manager de transacao implicita, MAS ha duas conexoes separadas na funcao:

1. Primeira `with get_conn()` (ln 295-299): le a base atual para calculo de diff
2. Segunda `with get_conn()` (ln 301-343): executa todas as escritas

Entre as duas conexoes existe uma janela de tempo onde outro processo poderia modificar o banco. Alem disso, o loop de UPSERT (ln 310-336) nao e guardado por tratamento de excecao — se falhar no registro N, os primeiros N-1 ja foram escritos mas o historico ainda nao foi inserido, deixando o banco em estado parcialmente atualizado.

**Correcao recomendada:**
- Unificar em uma unica conexao/transacao
- Adicionar try/except com conn.rollback() explicito em caso de erro

---

## Debitos Medios

### DB-M01 — Datas armazenadas como TEXT em formato DD/MM/YYYY

**Arquivo:** `database.py` — todas as funcoes que gravam datas

Colunas afetadas: `inadimplentes.ultimo_vencimento`, `inadimplentes.data_entrada`, `inadimplentes.data_atualizacao`, `envios.data_envio`, `historico_atualizacoes.data`.

O formato DD/MM/YYYY nao e ordenavel como string — `ORDER BY data_atualizacao` retorna resultados incorretos. O SQLite nao tem tipo DATE nativo mas suporta ISO 8601 (YYYY-MM-DD) com funcoes de data.

**Evidencia de problema em producao:**
```python
# database.py ln 323 — status_base
ult = conn.execute(
    "SELECT data FROM historico_atualizacoes WHERE empresa = ? ORDER BY id DESC LIMIT 1",
    (empresa,)
).fetchone()
```
A query ordena por `id` (sequencial), nao por `data` — workaround implicito para o problema de ordenacao de datas como TEXT.

**Correcao recomendada:** Converter para ISO 8601 (YYYY-MM-DD HH:MM:SS). Requer migracao de dados existentes.

---

### DB-M02 — Valores monetarios armazenados como REAL (ponto flutuante)

**Tabela:** `inadimplentes`
**Coluna:** `total REAL`
**Arquivo:** `database.py` ln 333 — `float(row['Total'])`

Ponto flutuante IEEE 754 introduz erros de arredondamento acumulativos. Para valores como R$ 1.234,50, o valor armazenado pode ser 1234.4999999999998 ou similar. Em somas agregadas (`SUM(total)`) o erro se propaga.

**Correcao recomendada:** Armazenar em INTEGER (centavos: 123450) ou usar TEXT com 2 casas decimais fixas. Requer ajuste nas queries e na camada de apresentacao.

---

### DB-M03 — Ausencia de tabela empresas — empresa como TEXT livre

**Arquivo:** `database.py` ln 13 — constante `EMPRESAS = ('INEPROTEC', 'MATRICULAEAD')`

Nao existe tabela `empresas` no banco. A validacao do valor de empresa e feita exclusivamente na camada Python pela constante `EMPRESAS`. Se um INSERT for feito diretamente no SQLite (ferramenta externa, script ad-hoc), qualquer string e aceita como empresa sem rejeicao pelo banco.

**Correcao recomendada:**
```sql
CREATE TABLE empresas (
    codigo TEXT PRIMARY KEY,
    nome   TEXT NOT NULL
);
INSERT INTO empresas VALUES ('INEPROTEC', 'Ineprotec');
INSERT INTO empresas VALUES ('MATRICULAEAD', 'Matricula EaD');
```
Adicionar CHECK constraint ou FK nas demais tabelas.

---

### DB-M04 — incrementar_cobrancas usa executemany sem transacao explicita

**Arquivo:** `database.py` ln 291-298 (`incrementar_cobrancas`)

```python
conn.executemany(
    "UPDATE inadimplentes SET qtd_cobranca = COALESCE(qtd_cobranca, 0) + 1 "
    "WHERE cpf = ? AND empresa = ?",
    [(cpf, empresa) for cpf in cpfs]
)
conn.commit()
```

O uso de `with get_conn() as conn:` com `conn.commit()` manual funciona, mas se `executemany` falhar apos processar N CPFs, o commit nao ocorre e nenhum CPF e atualizado — comportamento correto por atomicidade. Porem, nao ha tratamento de excecao explicito: a excecao vai subir para o caller sem mensagem contextualizada, dificultando diagnostico.

---

### DB-M05 — templates referenciados em envios por titulo (TEXT) em vez de id (INTEGER)

**Tabela:** `envios`
**Coluna:** `template_titulo TEXT`
**Arquivo:** `database.py` ln 356-360 (`registrar_envio`)

O historico de envios armazena o titulo do template como string livre, nao o `id` INTEGER. Se um template for renomeado via `salvar_template()` (ln 304-312), o historico de envios anteriores passa a referenciar um titulo inexistente, quebrando a rastreabilidade.

**Correcao recomendada:** Substituir `template_titulo TEXT` por `template_id INTEGER REFERENCES templates(id) ON DELETE SET NULL`.

---

## Debitos Baixos

### DB-B01 — get_conn nao habilita WAL mode

**Arquivo:** `database.py` ln 121-124 (`get_conn`)

O modo padrao do SQLite e journal_mode=DELETE (rollback journal). O modo WAL (Write-Ahead Logging) permite leituras concorrentes sem bloquear escritas, o que e benefico para um app Flask com multiplas requisicoes simultaneas.

**Correcao recomendada:** Adicionar em `get_conn()`:
```python
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
```

---

### DB-B02 — Ausencia de estrategia de backup documentada

Nao ha referencia a backup do arquivo `C:\MATINE\banco\inadimplencia.db` no codigo ou na documentacao do projeto. SQLite e um arquivo unico — uma falha de disco ou corrupção sem backup resulta em perda total dos dados.

**Correcao recomendada:**
- Backup diario automatico com copia rotacionada (ex: 7 dias)
- Alternativa: habilitar SQLite Online Backup API via `sqlite3.connect().backup()`
- Ou migrar para PostgreSQL com backup gerenciado

---

### DB-B03 — Coluna ativo em templates sem CHECK constraint

**Tabela:** `templates`
**Coluna:** `ativo INTEGER DEFAULT 1`

A coluna `ativo` e tratada como booleano (0 ou 1) mas o tipo INTEGER aceita qualquer valor inteiro. Um INSERT/UPDATE com `ativo = 2` seria aceito silenciosamente e causaria comportamento indefinido nas queries que filtram `WHERE ativo = 1`.

**Correcao recomendada:** `ativo INTEGER DEFAULT 1 CHECK (ativo IN (0, 1))`
Aplica-se tambem a `smtp_tls INTEGER DEFAULT 1` em `config_email`.

---

## Recomendacoes por Prioridade

### Prioridade 1 — Corrigir antes da proxima implantacao

| ID     | Acao | Estimativa |
|--------|------|-----------|
| DB-C01 | Criptografar smtp_senha com Fernet antes de persistir; revogar senhas atuais | 2h |
| DB-C02 | Ativar `PRAGMA foreign_keys = ON` em get_conn() e adicionar FKs logicas nas tabelas | 3h |
| DB-A01 | Criar tabela `schema_migrations` e separar migracoes em funcoes atomicas | 4h |

### Prioridade 2 — Corrigir no proximo sprint

| ID     | Acao | Estimativa |
|--------|------|-----------|
| DB-A02 | Criar indice composto em envios(empresa, data_envio) | 30min |
| DB-A03 | Criar indices em empresa nas 4 tabelas operacionais | 1h |
| DB-A04 | Refatorar salvar_base para usar conexao unica com rollback explicito | 2h |
| DB-M05 | Adicionar coluna template_id INTEGER em envios e deprecar template_titulo | 3h |

### Prioridade 3 — Melhorias planejadas

| ID     | Acao | Estimativa |
|--------|------|-----------|
| DB-M01 | Migrar datas para ISO 8601 | 4h (inclui migracao de dados) |
| DB-M02 | Converter total de REAL para INTEGER em centavos | 3h (inclui migracao de dados) |
| DB-M03 | Criar tabela empresas e adicionar FK/CHECK nas demais tabelas | 2h |
| DB-B01 | Habilitar WAL mode em get_conn() | 15min |
| DB-B02 | Implementar rotina de backup automatico do .db | 2h |
| DB-B03 | Adicionar CHECK constraint em colunas booleanas | 30min |

---

## Pontos Positivos

Para registro e balanco justo da auditoria, o codigo apresenta praticas corretas em:

- **Uso de parametros bind** em todas as queries inspecionadas — nao foi identificado SQL injection por concatenacao de string
- **UPSERT nativo** (INSERT ... ON CONFLICT DO UPDATE) em `salvar_base` e `salvar_config_email` — correto e eficiente
- **Separacao por empresa** como discriminador multi-tenant funcional — arquitetura shared database, separate schema-lite bem implementada
- **PK composta (cpf, empresa)** em `inadimplentes` — protecao contra duplicatas por tenant
- **UNIQUE constraint** em `config_email.empresa` — correto para relacao 1:1

---

*Auditoria realizada por Dara (@data-engineer) — Brownfield Discovery Fase 2*
*Projeto: MAT-INE Inadimplencia 2026*
