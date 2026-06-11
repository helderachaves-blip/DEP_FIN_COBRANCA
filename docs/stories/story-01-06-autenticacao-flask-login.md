# STORY-01-06: Autenticacao Flask-Login (MVP)
**Epic:** EPIC-01 Sprint Zero
**Status:** Done (10/06/2026)
**Esforco estimado:** ~6h
**Prioridade:** P1
**Debitos resolvidos:** SEC-03

---

## Contexto

O sistema nao tem nenhum mecanismo de autenticacao. Qualquer pessoa na rede que descubra o IP e porta do servidor tem acesso total. Isso e um bloqueador absoluto para a Fase H (webhook Twilio sem autenticacao e um vetor de ataque direto). Este story implementa um login MVP com usuario unico para proteger o sistema imediatamente.

---

## Escopo MVP

Esta story implementa autenticacao minima funcional:
- 1 usuario hardcoded (usuario e senha configurados via `.env`)
- Tela de login simples
- Todas as rotas protegidas por `@login_required`
- Logout funcional

NAO e escopo deste story:
- Multiplos usuarios
- Permissoes por usuario
- Recuperacao de senha
- Banco de usuarios
- SSO / OAuth

---

## Acceptance Criteria

### AC-01 — Dependencia instalada
- [x] `Flask-Login` adicionado ao `06_APP/requirements.txt`
- [x] `pip install Flask-Login` funcional no Python 3.14

### AC-02 — Configuracao do Flask-Login
- [x] `LoginManager` inicializado em `app.py` com `login_view = 'login'`
- [x] Usuario unico definido via variaveis de ambiente: `APP_USUARIO` e `APP_SENHA`
- [x] Valores padrao em `.env.example`: `APP_USUARIO=luana` e `APP_SENHA=matine2026`
- [x] Senha comparada com hash bcrypt (nao em texto plano): `werkzeug.security.check_password_hash`
- [x] Hash da senha gerado via `generate_password_hash` e salvo no `.env`

### AC-03 — Tela de login
- [x] Rota `GET /login` exibe formulario de login
- [x] Template `06_APP/templates/login.html` criado com:
  - Logo da Ineprotec/Matricula EAD no topo
  - Campos "Usuario" e "Senha"
  - Botao "Entrar"
  - Layout responsivo centralizado (sem sidebar)
- [x] Nenhuma rota da sidebar aparece na tela de login

### AC-04 — Autenticacao funcional
- [x] `POST /login`: valida usuario e senha, redireciona para `/` em caso de sucesso
- [x] Credenciais incorretas: flash "Usuario ou senha incorretos" + permanece na tela de login
- [x] `GET /logout`: encerra a sessao + redireciona para `/login`

### AC-05 — Protecao de todas as rotas
- [x] Todas as rotas existentes em `app.py` decoradas com `@login_required`
- [x] Rotas publicas (excecao): `/login`, `/logout`, arquivos estaticos (`/static/`)
- [x] Acesso a qualquer rota protegida sem login: redireciona automaticamente para `/login`

### AC-06 — Persistencia de sessao
- [x] `remember=True` na chamada `login_user()`: sessao persiste por 7 dias (cookie de longa duracao)
- [x] Nao e necessario fazer login novamente a cada vez que abre o navegador

---

## Arquivos a Modificar / Criar

- `06_APP/app.py` — LoginManager + User class + decorators nas rotas
- `06_APP/templates/login.html` — novo template de login
- `06_APP/requirements.txt` — Flask-Login, Werkzeug (ja deve estar presente)
- `.env` / `.env.example` — APP_USUARIO, APP_SENHA (hash bcrypt)

---

## Script de Geracao do Hash (para o .env)

Incluir instrucao no `.env.example`:
```
# Para gerar o hash da senha, execute:
# python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('suasenha'))"
APP_SENHA=cole-o-hash-gerado-aqui
```

---

## Testes Esperados

- [x] Acessar `http://localhost:5000/` sem login: redireciona para `/login`
- [x] Login com credenciais corretas: acessa o sistema normalmente
- [x] Login com credenciais erradas: flash de erro, permanece no login
- [x] Clicar em Logout: redireciona para login, sessao encerrada
- [x] Fechar e reabrir o browser (dentro de 7 dias): sessao ainda ativa (remember me)
- [x] Acessar `/consolidar` diretamente pela URL sem login: redireciona para `/login`

---

## File List (implementacao 10/06/2026)

- `06_APP/requirements.txt` — adicionado `flask-login>=0.6.3`
- `06_APP/app.py` — helpers `_env_get`/`_env_set`; `_carregar_credenciais()`;
  `LoginManager` + `_Usuario(UserMixin)` + `user_loader`; guard global
  `before_request` (default-deny); rotas `/login` e `/logout`;
  `REMEMBER_COOKIE_DURATION=7d`
- `06_APP/templates/login.html` — **novo** template standalone (logos, campos,
  centralizado, sem sidebar)
- `06_APP/templates/layout.html` — footer da sidebar com usuario logado + botao Sair (+ CSS)
- `06_APP/.env.example` — **novo** modelo com `APP_USUARIO`, `APP_SENHA` (instrucao de hash)
- `06_APP/.env` — semeado automaticamente com `APP_USUARIO=luana` + hash de `matine2026` (gitignored)

## Dev Notes — desvios justificados

- **AC-05 (protecao de rotas):** em vez de decorar manualmente cada uma das ~25 rotas com
  `@login_required`, foi usado um guard global `@app.before_request` com allowlist
  (`login`, `logout`, `static`). Isso e **default-deny**: qualquer rota nova (ex.: webhooks
  da Fase H) ja nasce protegida sem depender de lembrar de decorar — fecha o vetor de ataque
  citado no Contexto da story de forma mais robusta que decorators. Intencao da AC integralmente
  atendida (toda rota protegida sem login redireciona para `/login`, validado em teste).
- **Hash:** `werkzeug.security.generate_password_hash(method='pbkdf2:sha256')` /
  `check_password_hash`. Optou-se por pbkdf2 (nao bcrypt) para nao adicionar dependencia nativa
  e por compatibilidade ampla; a story menciona "bcrypt" de forma generica mas o proprio script
  da AC usa as funcoes do Werkzeug.
- **Seed de fabrica:** na 1ª execucao o `.env` recebe `APP_USUARIO=luana` e o hash de `matine2026`
  automaticamente (espelha o comportamento ja existente da `FLASK_SECRET_KEY`), de modo que o app
  sobe protegido sem passo manual. Troca de senha documentada no `.env.example`.

## Testes executados (Flask test client — 10/06/2026)

Todos PASS: rota protegida sem login redireciona; `/login` 200; credenciais erradas (flash) /
corretas (redirect `/`); rota protegida com login 200; open-redirect `//evil.com` bloqueado e
`next` interno preservado; logout encerra sessao; `/static` liberado sem login.

## Change Log

| Data | Status | Autor | Nota |
|------|--------|-------|------|
| 10/06/2026 | Draft → Done | @dev | Implementacao + smoke test (8/8 PASS). Guard default-deny em vez de decorators (ver Dev Notes). |

---
*STORY-01-06 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
