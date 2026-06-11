# PLANO DE AÇÃO — MAT-INE Inadimplência 2026

> Sprint atual e próximos passos. Atualizar a cada sessão.
> Quando um item é entregue: marca ✅ aqui e registra no ROADMAP.md.
> Última atualização: 10/06/2026

---

## Estado Atual

- **Branch:** `homologacao`
- **Fase do produto:** Fases A–G concluídas. **EPIC-01 (Sprint Zero) COMPLETO — 7 de 7 stories** (01-01 a 01-07). Próximo marco: **Fase H** (integrações automáticas).
- **Extra (10/06 noite):** Central de Ajuda (`/ajuda`) — índice lateral + conteúdo operacional por tela. Ver `docs/stories/story-ajuda-central.md`.
- **Extra (10/06 noite):** Gestão de múltiplos usuários — autenticação migrada do `.env` para a tabela `usuarios` (migration 007); telas `/usuarios` (admin) e `/conta` (trocar própria senha); admin inicial `luana` semeado do `.env`. Ver `docs/stories/story-multiusuario.md`.
- **⚠️ Reiniciar o app** para ver as novidades (templates ficam em cache com `debug=False`).
- **Último commit no remoto:** `2719016` (será atualizado ao push do multiusuário).
- **App:** roda com `python app.py` em `06_APP/` → http://localhost:5000. Estrutura `C:\MATINE` criada automaticamente no startup; `.env` (gitignored) gerado na 1ª execução com a `FLASK_SECRET_KEY`.
- **Sessão 10/06/2026 (manhã):** Correções de UI (R1/R2/B1/B2) + STORY-01-01 (Quick Wins) + STORY-01-02 (Indicadores de empresa). Nova STORY-01-07 (first-run setup) adicionada ao backlog.
- **Sessão 10/06/2026 (tarde):** STORY-01-03 (Loading states) + STORY-01-05 (Schema migrations + índices + WAL) + STORY-01-04 (senha SMTP via keyring). Banco real de produção migrado (versionamento + WAL + senha movida ao keyring); backup `inadimplencia_backup_20260610_204730.db` criado. Regra de sincronia git↔plano adicionada ao frame global (`~/.claude/CLAUDE.md`).

---

## O Que Está Pendente de Commit / Push

Nada pendente de commit. **Nada aguardando push** — `origin/homologacao` e `HEAD`
idênticos (`git rev-list --left-right --count origin/homologacao...HEAD` = `0  0`,
verificado em 10/06/2026 noite).

**Últimos pushes** (sessão 10/06 noite, via @devops):
- `8d257a2..18909c9` — 9 commits: STORY-01-03/04/05 + `docs:` de rastreio
- `855a58d..ace5172` — STORY-01-06 (Autenticação Flask-Login) + plano/roadmap
- `d1c91ea..c5fe5d8` — STORY-01-07 (First-run setup) → **EPIC-01 completo**
- `78f6b4c..2719016` — Central de Ajuda (`/ajuda`)

Topo do remoto = `2719016`. (recompute sempre com `git fetch` — não confie nesta lista.)

---

## Correções de UI Reportadas (10/06/2026) — ✅ ENTREGUE

Bugs e ajustes verificados durante a revisão do app. Resolvidos na sessão de 10/06/2026
(100% template + JS, sem mudança de backend). Validados com app rodando (HTTP 200 em
`/resultado` e `/base`).

### Aba Resultados (`resultado.html`)

| # | Item | Solução | Status |
|---|------|---------|--------|
| R1 | Botões **"Vence Hoje"** e **"À Vencer"** não filtravam | Cards ganharam `stat-filtro` + `data-filtro`; `filtrar()` estendido para varrer também a tabela `#tabelaAvencer` (com toggle de seção: categoria à vencer oculta a tabela de inadimplentes e vice-versa). | ✅ |
| R2 | Dropdown **Filtrar** com categorias incompletas | `#filtroCategoria` passou a listar **Vence Hoje** e **A Vencer** (dentro de `{% if avencer_linhas %}`). | ✅ |

### Aba Base (`base.html`)

| # | Item | Solução | Status |
|---|------|---------|--------|
| B1 | Remover legendas da 3ª linha | Badges INADIMPLENTE / QUITADO / RENEGOCIADO removidos; texto de ajuda "Clique em Alterar Status…" mantido. | ✅ |
| B2 | Dropdown **Filtrar** com categorias incompletas | `#filtroCategoria` ganhou **Vence Hoje** e **A Vencer**; JS mapeia para as flags `data-vence-hoje`/`data-ren` (Base não usa `data-cat` para essas). A Vencer = na sessão À Vencer e não vence hoje. | ✅ |

**Pendente:** commit local na branch `homologacao` (push é do @devops).

---

## EPIC-01 — Sprint Zero (Pré-Fase H)

Todos os débitos abaixo são pré-requisitos para a Fase H. Nenhuma nova funcionalidade de integração (WhatsApp automático, Kommo, Synapta API) deve ser iniciada antes do EPIC-01 estar completo.

| Story | Título | Esforço | Status |
|-------|--------|---------|--------|
| 01-01 | Quick Wins — encoding, cores, títulos, confirmações, secret key | ~7h | ✅ Done |
| 01-02 | Indicadores de empresa ativa (topbar + wizard) | ~3h | ✅ Done |
| 01-03 | Loading states + confirmação "Atualizar Base" | ~5h | ✅ Done |
| 01-04 | Proteger senha SMTP com Python Keyring | ~4h | ✅ Done |
| 01-05 | Schema migrations + índices + WAL mode | ~12h | ✅ Done |
| 01-06 | Autenticação Flask-Login (MVP — usuário único) | ~6h | ✅ Done |
| 01-07 | First-run setup robusto (estrutura `C:\MATINE` + onboarding dev) | ~3h | ✅ Done |

**Total estimado: ~40h — EPIC-01 COMPLETO (7/7) ✅**

---

## Detalhe das Stories

### STORY-01-01 — Quick Wins (~7h) — ✅ ENTREGUE (10/06/2026)
- ✅ Encoding UTF-8 no `layout.html` (sem BOM) — **já estava OK** (charset UTF-8 + zero BOM em todos os templates)
- ✅ Cores semânticas por categoria em `resultado.html` e `envio_mensagens.html` — **já estava OK** (badges/cores Novo·Mês·+30d·Vence Hoje)
- ✅ Título dinâmico por página (`{% block title %}` em `layout.html` + 5 templates filhos)
- ✅ Confirmação modal antes de "Limpar Sessão" (modal Bootstrap em `index.html`; base não é afetada)
- ✅ `secret_key` Flask via `.env` — função `_carregar_secret_key()` em `app.py` gera `secrets.token_hex(32)` uma vez e persiste em `06_APP/.env` (gitignored); leitura manual, sem dependência nova

**Notas:** banner do console ainda sai com encoding cp1252 (cosmético, só no terminal — fora de escopo). Flask exibe dica "Install python-dotenv" ao ver o `.env`; ignorável (leitura é manual).

### STORY-01-02 — Indicadores de Empresa (~3h) — ✅ ENTREGUE (10/06/2026)
- ✅ Nome da empresa em texto na topbar, acima do toggle (azul `#42A5F5` = Ineprotec, verde `#66BB6A` = Mat. EaD)
- ✅ Banner persistente no topo do wizard de envio: "Enviando para: [EMPRESA]" com cor da empresa
- ✅ Confirmação (`confirm`) ao trocar empresa quando há consolidação ativa; novo flag `sessao_ativa` no context processor (`_estado_file(emp).exists()`)

### STORY-01-03 — Loading States (~5h) — ✅ ENTREGUE (10/06/2026)
- ✅ Spinner + botão desabilitado em todos os form POST síncronos: Consolidar, Gerar Relatório, Atualizar Base, Importar Alunos, Salvar SMTP, Testar SMTP — via handler global reutilizável em `layout.html` (`<form data-loading>` + `data-loading-text`)
- ✅ Modal de confirmação antes de "Comparar e Atualizar Base" (`#modalAtualizarBase`)
- ✅ Flash com contagem total de mensagens após "Gerar Relatórios"
- **Desvios justificados:** resultado.html não tem botão Atualizar Base (removido nas MUDANÇAS 1-5); Importar Alunos posta em `/upload` (não `/upload-alunos`); `/gerar-relatorio` redireciona para `/resultado` (MUDANÇAS 1-5) — flash mantido no destino atual

### STORY-01-04 — Senha SMTP Segura (~4h) — ✅ ENTREGUE (10/06/2026)
- ✅ Senha SMTP movida do SQLite para o keyring (Windows Credential Store, backend WinVaultKeyring)
- ✅ Coluna `smtp_senha` guarda só o marcador `[keyring]` (senha real nunca no banco)
- ✅ Migração automática no startup move senha legada em texto plano → keyring (banco real migrado)
- ✅ UI: campo senha não vaza no HTML; bullets quando configurada; vazio preserva a atual
- ✅ Fallback de rollback: variável de ambiente `SMTP_<EMPRESA>_SENHA`
- **Nota:** coluna mantida (com marcador) por compatibilidade em vez de removida — evita migração de schema destrutiva; serve de fallback se o keyring falhar antes da migração

### STORY-01-05 — Schema Migrations (~12h) — ✅ ENTREGUE (10/06/2026)
- ✅ Tabela `schema_migrations` (version, name, applied_at) criada antes de tudo
- ✅ `init_db()` refatorado: runner aplica só migrations pendentes (`06_APP/migrations/` com 001–006)
- ✅ 5 índices de performance (migration 005); WAL + `foreign_keys=ON` em `get_conn()` (migration 006 fixa WAL)
- ✅ Detecção de banco legado: 001–004 marcadas como aplicadas sem re-executar; 005/006 rodam
- ✅ Migração automática no startup; banco real de produção migrado sem perda (1024 registros; backup criado)
- **Nota:** índices implementados foram `empresa` por tabela + `(empresa, data_envio)` em envios (mais alinhados às queries reais do app que os `(empresa,status)/(empresa,categoria)` do rascunho original)

### STORY-01-06 — Autenticação Flask-Login (~6h) — ✅ ENTREGUE (10/06/2026)
- ✅ Flask-Login + usuário único via `.env` (`APP_USUARIO`/`APP_SENHA`); senha como hash pbkdf2 (nunca em texto plano)
- ✅ Login/logout funcionais; `remember=True` com cookie de 7 dias
- ✅ Proteção de **todas** as rotas via guard global `@app.before_request` (default-deny; allowlist: login/logout/static) — mais robusto que decorar 25 rotas, e fecha o vetor da Fase H (webhooks já nascem protegidos)
- ✅ Tela de login standalone (`login.html`, logos, centralizada, sem sidebar) + footer da sidebar com usuário logado e botão Sair
- ✅ Seed de fábrica na 1ª execução: `luana` / `matine2026` (troca documentada no `.env.example`)
- ✅ Smoke test via Flask test client: 8/8 PASS (inclui bloqueio de open-redirect)
- **Desvio justificado:** `before_request` no lugar de `@login_required` por rota (ver Dev Notes da story)

### STORY-01-07 — First-run setup robusto (~3h)
### STORY-01-07 — First-run setup robusto (~3h) — ✅ ENTREGUE (10/06/2026)
- ✅ Função `setup_inicial()` idempotente encapsula a criação (antes solta no import); chamada uma vez via `PRIMEIRA_EXECUCAO = setup_inicial()`
- ✅ Passos: (1) cria estrutura `C:\MATINE`, (2) `db.init_db()` (schema versionado + templates padrão), (3) seeding já idempotente dentro do init_db, (4) `_checar_dependencias()` com mensagem amigável (sem stack trace cru)
- ✅ Detecção de 1ª execução pela ausência do banco; banner do `__main__` sinaliza + loga; retorna `True`/`False`
- ✅ `06_APP/README.md` reescrito (onboarding web atual: Python 3.10+, deps, `python app.py`, login padrão, troca de senha)
- **Notas:** seeding de templates já existia no `init_db`; `secret_key` já tinha ido para `.env` na 01-01 (nada a mover)

---

## Ordem de Implementação Recomendada

```
01-01 → 01-02 → 01-03   ✅ (independentes, UX)
01-05                    ✅ (banco — feito antes de 01-04 e 01-06)
01-04                    ✅ (segurança — senha SMTP no keyring)
01-06                    ✅ (autenticação Flask-Login)
01-07                    ✅ (first-run setup robusto — EPIC-01 FECHADO)
```

---

## Próxima Sessão

1. ✅ Correções de UI (R1/R2/B1/B2) — commitadas (`0e88c5b`)
2. ✅ STORY-01-01 (Quick Wins) — entregue
3. ✅ STORY-01-02 (Indicadores de empresa ativa) — entregue
4. ✅ STORY-01-03 (Loading states) — entregue
5. ✅ STORY-01-05 (Schema migrations + índices + WAL) — entregue
6. ✅ STORY-01-04 (Senha SMTP via Keyring) — entregue
7. ✅ STORY-01-06 (Autenticação Flask-Login) — entregue
8. ✅ STORY-01-07 (First-run setup robusto) — entregue → **EPIC-01 COMPLETO**
9. Próxima sessão: iniciar **Fase H** (integrações automáticas). Recomendado começar
   pelo PRD/spec da integração WhatsApp (escolha do provider: WAHA / Evolution / Z-API / Twilio)
   antes de implementar — ver tabela "Fase H" abaixo.

---

## Bloqueios

Nenhum bloqueio ativo.

---

## Fase H — Após EPIC-01

| Item | Dependência |
|------|------------|
| WhatsApp automático (WAHA / Evolution API / Z-API / Twilio) | EPIC-01 completo |
| Link de pagamento dinâmico por aluno (API Synapta) | EPIC-01 completo |
| Kommo CRM — tagging automático via API | EPIC-01 + autenticação |
| Agendamento diário/semanal | EPIC-01 + WhatsApp |
