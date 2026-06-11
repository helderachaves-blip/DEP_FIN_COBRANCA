# STORY-01-07: First-run setup robusto
**Epic:** EPIC-01 Sprint Zero
**Status:** Done (10/06/2026)
**Esforco estimado:** ~3h
**Prioridade:** P2
**Debitos resolvidos:** OPS-01

---

## Contexto

O projeto e compartilhado com colaborador de desenvolvimento (Helder). Em outra maquina
o caminho do projeto muda, mas o app usa `DATA_DIR = C:\MATINE` (fixo). A estrutura ja era
criada no startup, porem de forma solta no import do modulo (sem encapsulamento, sem deteccao
de primeira execucao, sem mensagem amigavel se faltar dependencia). Esta story torna o
onboarding explicito e a prova de falhas. **Fecha o EPIC-01.**

---

## Acceptance Criteria

### AC-01 — Funcao setup_inicial() idempotente
- [x] Criacao da estrutura encapsulada numa funcao `setup_inicial()` (antes era solta no import)
- [x] Idempotente: seguro chamar a cada boot; todas as operacoes usam `exist_ok=True` / `INSERT` condicional
- [x] Chamada uma vez no carregamento do modulo: `PRIMEIRA_EXECUCAO = setup_inicial()`

### AC-02 — Passos do setup
- [x] (1) Cria a estrutura `C:\MATINE` (uploads por empresa/tipo, relatorios, estado, logs, banco, crm-exports)
- [x] (2) `db.init_db()` — schema versionado (migrations) + templates padrao por empresa (ja idempotente)
- [x] (3) Templates padrao semeados por empresa (via `db._seed_templates_padrao`, dentro do init_db)
- [x] (4) Valida dependencias e exibe mensagem amigavel em vez de stack trace cru

### AC-03 — Deteccao de primeira execucao
- [x] Detecta "primeira execucao" pela ausencia do banco (`not db.DB_PATH.exists()`)
- [x] Loga/sinaliza setup concluido; banner do `__main__` avisa quando foi a 1a execucao
- [x] `setup_inicial()` retorna `True` na primeira execucao, `False` nas seguintes

### AC-04 — Validacao de dependencias amigavel
- [x] `_checar_dependencias()` roda antes de importar libs de terceiros
- [x] Se faltar `flask`/`flask_login`/`pandas`/`openpyxl`: imprime instrucao (`pip install -r requirements.txt`) e sai com codigo 1, sem ImportError cru

### AC-05 — Onboarding documentado no README
- [x] `06_APP/README.md` reescrito: Python 3.10+, `pip install -r requirements.txt`, `python app.py`, acesso em `localhost:5000`
- [x] Documenta criacao automatica da estrutura, credenciais padrao e troca de senha (relacao com 01-06)

---

## Arquivos Modificados / Criados

- `06_APP/app.py` — `_checar_dependencias()`; constantes `BANCO_DIR`/`CRM_PASTA` consolidadas
  no topo; bloco de init solto -> funcao `setup_inicial()` + `PRIMEIRA_EXECUCAO`; banner do
  `__main__` sinaliza 1a execucao + login padrao
- `06_APP/README.md` — reescrito (onboarding web atual, antes era da versao desktop antiga)

## Dev Notes

- O seed de templates padrao (passo 3) ja existia dentro de `db.init_db()`
  (`_seed_templates_padrao`, idempotente) — `setup_inicial()` apenas o orquestra, sem duplicar.
- A `secret_key` fixa ja havia sido movida para `.env` na STORY-01-01; nao havia o que mover aqui.
- `_checar_dependencias()` usa `importlib.util.find_spec` (nao importa de fato) — barato e
  roda antes dos imports pesados, garantindo a mensagem amigavel.

## Testes executados (10/06/2026)

Todos PASS: import limpo; `setup_inicial()` idempotente (2a chamada retorna False, nao quebra);
estrutura de pastas presente; fluxo de login intacto pos-refactor; `_checar_dependencias()` ok
com todas as deps presentes.

## Change Log

| Data | Status | Autor | Nota |
|------|--------|-------|------|
| 10/06/2026 | Draft -> Done | @dev | Encapsulamento do setup + dep check + README. Fecha o EPIC-01. |

---
*STORY-01-07 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
