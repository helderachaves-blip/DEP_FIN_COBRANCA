# STORY-TESTES: Suíte de testes automatizados (pytest)
**Epic:** Qualidade & Fundação (pré-Fase H)
**Status:** Done (10/06/2026)
**Esforco estimado:** ~5h
**Prioridade:** P1

---

## Contexto

O app não tinha testes automatizados — toda validação era smoke test manual. Antes da
Fase H (que vai mexer pesado no banco e em integrações externas), uma rede de regressão
é o investimento técnico de maior retorno e não depende de decisões de produto.

---

## Acceptance Criteria

- [x] Caminho de dados configurável por `MATINE_DATA_DIR` (default `C:\MATINE` — produção inalterada), em `app.py` e `database.py`, para os testes rodarem **isolados** do banco real
- [x] `conftest.py` define `MATINE_DATA_DIR` para um temp **antes** de importar app/database; remove o temp ao fim
- [x] Fixtures: `app`, `client`, `db`, `users` (reseta tabela e cria admin/operador conhecidos), `login`
- [x] `pytest.ini` (`testpaths=tests`, `pythonpath=.`) + `requirements-dev.txt` (pytest)
- [x] `tests/test_processing.py` — fmt_brl, _converter_valor, detectar_tratamento, _SafeFormat, _slugify, consolidar (CSV `,` e `;`, sem-cadastro, arquivo inválido)
- [x] `tests/test_migrations.py` — schema completo pós-init, runner fresh + idempotente, up/down da migration 007
- [x] `tests/test_auth.py` — guard de rota, página de login, credenciais erradas/certas, logout, /static público, open-redirect bloqueado, next interno
- [x] `tests/test_usuarios.py` — admin lista, operador barrado, criar (+ duplicado + senha curta), resetar senha, anti-lockout (própria conta, último admin), remover
- [x] `tests/test_conta.py` — editar próprio nome, trocar senha (atual errada/curta/confirmação/sucesso + re-login)
- [x] **49 testes passando** (`pytest` verde)
- [x] README com seção Testes; `.gitignore` ignora `.pytest_cache`

## Arquivos Criados / Modificados

- `06_APP/app.py` — `DATA_DIR` lê `MATINE_DATA_DIR`
- `06_APP/database.py` — `DATA_DIR`/`DB_PATH` leem `MATINE_DATA_DIR`
- `06_APP/conftest.py`, `06_APP/pytest.ini`, `06_APP/requirements-dev.txt` — **novos**
- `06_APP/tests/test_processing.py` · `test_migrations.py` · `test_auth.py` · `test_usuarios.py` · `test_conta.py` — **novos**
- `06_APP/README.md` — seção Testes; `.gitignore` — `.pytest_cache`

## Dev Notes

- **Isolamento é a peça-chave:** o `DATA_DIR`/`DB_PATH` eram hardcoded em `C:\MATINE`; sem
  parametrização, importar o app nos testes migraria/semearia o banco real. A variável
  `MATINE_DATA_DIR` (default inalterado) resolve isso e ainda melhora a portabilidade
  (relacionado à STORY-01-07).
- A fixture `users` reseta a tabela `usuarios` por teste e cria admin/operador com senhas
  conhecidas — testes determinísticos e independentes do seed do `.env`.
- Suíte leva ~160s: dominada pelo hash pbkdf2 (600k iterações) repetido em muitos logins/criações.
  Aceitável; se incomodar, dá para usar um método de hash mais rápido só em teste.
- Warning de `datetime.utcnow()` vem do Flask-Login (interno), não do nosso código.

## Como rodar

```
cd 06_APP
pip install -r requirements-dev.txt
pytest
```

## Change Log

| Data | Status | Autor | Nota |
|------|--------|-------|------|
| 10/06/2026 | Draft -> Done | @dev | 49 testes (processing/migrations/auth/usuarios/conta), banco isolado via MATINE_DATA_DIR. |

---
*STORY-TESTES — Qualidade & Fundação — MAT-INE Inadimplencia 2026*
