# PLANO DE AÇÃO — MAT-INE Inadimplência 2026

> Sprint atual e próximos passos. Atualizar a cada sessão.
> Quando um item é entregue: marca ✅ aqui e registra no ROADMAP.md.
> Última atualização: 10/06/2026

---

## Estado Atual

- **Branch:** `homologacao`
- **Fase do produto:** Fases A–G concluídas. EPIC-01 (Sprint Zero) em andamento — **2 de 6 stories entregues** (01-01, 01-02).
- **Último commit:** `6d641b9` — STORY-01-02 (indicadores de empresa)
- **App:** roda com `python app.py` em `06_APP/` → http://localhost:5000. Estrutura `C:\MATINE` criada automaticamente no startup; `.env` (gitignored) gerado na 1ª execução com a `FLASK_SECRET_KEY`.
- **Sessão 10/06/2026:** Correções de UI (R1/R2/B1/B2) + STORY-01-01 (Quick Wins) + STORY-01-02 (Indicadores de empresa). Nova STORY-01-07 (first-run setup) adicionada ao backlog.

---

## O Que Está Pendente de Commit

Nada pendente de commit. **3 commits locais aguardam push (exclusivo do @devops):**
- `0e88c5b` — correções de UI (R1/R2/B1/B2)
- `2e73302` — STORY-01-01 (Quick Wins)
- `6d641b9` — STORY-01-02 (Indicadores de empresa)

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
| 01-03 | Loading states + confirmação "Atualizar Base" | ~5h | Draft |
| 01-04 | Proteger senha SMTP com Python Keyring | ~4h | Draft |
| 01-05 | Schema migrations + índices + WAL mode | ~12h | Draft |
| 01-06 | Autenticação Flask-Login (MVP — usuário único) | ~6h | Draft |
| 01-07 | First-run setup robusto (estrutura `C:\MATINE` + onboarding dev) | ~3h | Draft |

**Total estimado: ~40h**

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

### STORY-01-03 — Loading States (~5h)
- Spinner + botão desabilitado em todos os form POST síncronos: Consolidar, Gerar Relatório, Atualizar Base, Importar Alunos, Salvar SMTP, Testar SMTP
- Modal de confirmação antes de "Comparar e Atualizar Base"
- Flash message com contagem de mensagens após "Gerar Relatórios"

### STORY-01-04 — Senha SMTP Segura (~4h)
- Migrar senha SMTP do SQLite para Python Keyring
- Remover campo `senha` da tabela `config_email`
- UI de Configurações: campo senha permanece mas não é lido do banco

### STORY-01-05 — Schema Migrations (~12h)
- Tabela `schema_migrations` para controle de versão do banco
- Índices: `(empresa, status)`, `(empresa, categoria)`, `(cpf, empresa)`
- WAL mode habilitado no `init_db()`
- Migration automática na inicialização

### STORY-01-06 — Autenticação Flask-Login (~6h)
- Tabela `usuarios` com usuário admin único
- Login/logout com Flask-Login
- Proteção de todas as rotas com `@login_required`
- Tela de login minimalista

### STORY-01-07 — First-run setup robusto (~3h)
**Motivação:** projeto compartilhado com colaborador de desenvolvimento. Em outra máquina o
caminho do projeto muda, mas o app usa `DATA_DIR = C:\MATINE` (fixo, `app.py:27`). A estrutura
já é criada no startup (`app.py:182-190` + `db.init_db()`), então o colega só precisa de Python
+ deps — o banco vazio é aceitável para dev. Esta story torna esse onboarding explícito e à prova de falhas.

- Encapsular a criação atual (hoje no import do módulo) numa função `setup_inicial()` idempotente
- Passos da função: (1) criar estrutura `C:\MATINE`, (2) `db.init_db()`, (3) semear templates
  padrão por empresa, (4) validar dependências e exibir mensagem amigável no primeiro acesso
  (em vez de stack trace cru)
- Detectar "primeira execução" (ex.: ausência do banco) e logar/sinalizar setup concluído
- Relação com 01-01: mover `secret_key` fixa (`app.py:38`) para `.env`
- **Onboarding dev (documentar no README):** instalar Python 3.10+, `pip install -r requirements.txt`,
  `python app.py`, acessar `http://localhost:5000` — estrutura criada automaticamente

---

## Ordem de Implementação Recomendada

```
01-01 → 01-02 → 01-03   (independentes, UX — fazer em sequência)
01-05                    (banco — fazer antes de 01-04 e 01-06)
01-04 → 01-06            (segurança — após migrations)
```

---

## Próxima Sessão

1. ✅ Correções de UI (R1/R2/B1/B2) — commitadas (`0e88c5b`)
2. ✅ STORY-01-01 (Quick Wins) — entregue
3. ✅ STORY-01-02 (Indicadores de empresa ativa) — entregue
4. Próxima: STORY-01-03 (Loading states). Sequência: 01-03 → 01-05 → 01-04 → 01-06 → 01-07

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
