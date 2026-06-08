# STORY-01-06: Autenticacao Flask-Login (MVP)
**Epic:** EPIC-01 Sprint Zero
**Status:** Draft
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
- [ ] `Flask-Login` adicionado ao `06_APP/requirements.txt`
- [ ] `pip install Flask-Login` funcional no Python 3.14

### AC-02 — Configuracao do Flask-Login
- [ ] `LoginManager` inicializado em `app.py` com `login_view = 'login'`
- [ ] Usuario unico definido via variaveis de ambiente: `APP_USUARIO` e `APP_SENHA`
- [ ] Valores padrao em `.env.example`: `APP_USUARIO=luana` e `APP_SENHA=matine2026`
- [ ] Senha comparada com hash bcrypt (nao em texto plano): `werkzeug.security.check_password_hash`
- [ ] Hash da senha gerado via `generate_password_hash` e salvo no `.env`

### AC-03 — Tela de login
- [ ] Rota `GET /login` exibe formulario de login
- [ ] Template `06_APP/templates/login.html` criado com:
  - Logo da Ineprotec/Matricula EAD no topo
  - Campos "Usuario" e "Senha"
  - Botao "Entrar"
  - Layout responsivo centralizado (sem sidebar)
- [ ] Nenhuma rota da sidebar aparece na tela de login

### AC-04 — Autenticacao funcional
- [ ] `POST /login`: valida usuario e senha, redireciona para `/` em caso de sucesso
- [ ] Credenciais incorretas: flash "Usuario ou senha incorretos" + permanece na tela de login
- [ ] `GET /logout`: encerra a sessao + redireciona para `/login`

### AC-05 — Protecao de todas as rotas
- [ ] Todas as rotas existentes em `app.py` decoradas com `@login_required`
- [ ] Rotas publicas (excecao): `/login`, `/logout`, arquivos estaticos (`/static/`)
- [ ] Acesso a qualquer rota protegida sem login: redireciona automaticamente para `/login`

### AC-06 — Persistencia de sessao
- [ ] `remember=True` na chamada `login_user()`: sessao persiste por 7 dias (cookie de longa duracao)
- [ ] Nao e necessario fazer login novamente a cada vez que abre o navegador

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

- [ ] Acessar `http://localhost:5000/` sem login: redireciona para `/login`
- [ ] Login com credenciais corretas: acessa o sistema normalmente
- [ ] Login com credenciais erradas: flash de erro, permanece no login
- [ ] Clicar em Logout: redireciona para login, sessao encerrada
- [ ] Fechar e reabrir o browser (dentro de 7 dias): sessao ainda ativa (remember me)
- [ ] Acessar `/consolidar` diretamente pela URL sem login: redireciona para `/login`

---

*STORY-01-06 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
