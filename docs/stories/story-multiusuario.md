# STORY-MULTIUSUARIO: Gestão de múltiplos usuários
**Epic:** Suporte & UX (pós-EPIC-01)
**Status:** Done (10/06/2026)
**Esforco estimado:** ~5h
**Prioridade:** P1
**Evolui:** STORY-01-06 (de usuário único .env → multi-usuário no banco)

---

## Contexto

A STORY-01-06 entregou autenticação de **usuário único** com credenciais no `.env`, sem tela
de cadastro. Helder pediu a evolução para **múltiplos usuários** (login por pessoa), com
cadastro/remoção e troca de senha pela interface. Isto move a autenticação do `.env` para o
banco e adiciona gestão.

---

## Acceptance Criteria

- [x] Migration `007_add_usuarios` cria a tabela `usuarios` (id, usuario único, nome, senha_hash, is_admin, ativo, criado_em)
- [x] **Bootstrap sem lockout:** na 1ª execução com a tabela vazia, o usuário do `.env`
      (`APP_USUARIO`/`APP_SENHA`) vira o **admin inicial** (`seed_usuario_admin`, idempotente)
- [x] Login e `user_loader` passam a consultar o banco (não mais o `.env`)
- [x] Senha sempre como hash pbkdf2 (`werkzeug.security`); nunca em texto plano
- [x] Tela `/usuarios` (admin): listar, criar (com flag admin), redefinir senha, promover/rebaixar, remover
- [x] Tela `/conta` (qualquer usuário): trocar a própria senha (confere a senha atual; mín. 6 caracteres)
- [x] Decorator `_admin_required`: rotas de gestão restritas a admins; não-admin é redirecionado
- [x] Proteções anti-lockout: não remover/rebaixar o **último admin**; não remover a **própria conta**
- [x] Sidebar: link "Usuários" no submenu Configurações (só admin); nome do usuário no rodapé vira link para "Minha conta"

## Arquivos Criados / Modificados

- `06_APP/migrations/007_add_usuarios.py` — **novo** (tabela `usuarios` + índice)
- `06_APP/database.py` — funções: `seed_usuario_admin`, `get_usuario_por_login`,
  `get_usuario_por_id`, `listar_usuarios`, `criar_usuario`, `atualizar_senha_usuario`,
  `set_usuario_admin`, `remover_usuario`, `is_ultimo_admin`
- `06_APP/app.py` — `_Usuario` carrega do banco; `user_loader`/`login` via banco;
  `_admin_required`; seed no `setup_inicial()`; rotas `/conta` e `/usuarios` (+4 ações)
- `06_APP/templates/usuarios.html` — **novo** (tabela + modais de criar/redefinir senha)
- `06_APP/templates/conta.html` — **novo** (trocar a própria senha)
- `06_APP/templates/layout.html` — link "Usuários" (admin) + nome→/conta no rodapé

## Dev Notes

- **Papel do `.env` agora:** `APP_USUARIO`/`APP_SENHA` servem **apenas como semente** do primeiro
  admin. Depois que a tabela tem ao menos um usuário, o login é 100% pelo banco — editar o `.env`
  não muda mais credenciais. Gestão passa a ser pela tela `/usuarios`.
- **Perfis:** simples (`is_admin` 0/1). Admin gerencia usuários; operador usa o sistema e troca a
  própria senha. Permissões granulares por função ficam como evolução futura (ROADMAP).
- **Sessões antigas:** quem estava logado pelo modelo antigo (id = nome de usuário) é deslogado
  no próximo acesso (o `user_loader` agora espera id numérico do banco) — basta logar de novo.

## Testes executados (10/06/2026)

9/9 PASS: migration aplicada + admin seedado; login admin; `/usuarios` lista; criar operador;
login operador; operador barrado em `/usuarios`; operador troca a própria senha + re-login;
`is_ultimo_admin` protege; limpeza. `py_compile` OK nos 3 arquivos.

## Change Log

| Data | Status | Autor | Nota |
|------|--------|-------|------|
| 10/06/2026 | Draft -> Done | @dev | Multi-usuário no banco (migration 007), telas /usuarios e /conta, proteções anti-lockout. |

---
*STORY-MULTIUSUARIO — Suporte & UX — MAT-INE Inadimplencia 2026*
