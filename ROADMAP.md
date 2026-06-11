# ROADMAP — MAT-INE Inadimplência 2026

> Linha do tempo completa. Itens entregues nunca são deletados — apenas marcados ✅.
> Última atualização: 10/06/2026

---

## ✅ FASE A — UX Rápidos (03/06/2026)

- [x] Alinhamento `text-end` + `text-nowrap` nas colunas de valores
- [x] Importação de Alunos movida para Configurações
- [x] Botão "Limpar Base" com modal de confirmação (digitar "LIMPAR")
- [x] Aviso de alunos sem cadastro após consolidação (flash warning)
- [x] Pastas de mês com nome por extenso: `01-Janeiro` … `12-Dezembro`

---

## ✅ FASE B — Redesign Layout Sidebar (03/06/2026)

- [x] Sidebar escura (`#1a1a2e`) substituindo navbar horizontal
- [x] "Cobranças INE-MAT" no topo da sidebar
- [x] Topbar com logos Ineprotec (esq) e Matrícula EaD (dir) com opacidade dinâmica

---

## ✅ FASE C — Categorias + Filtros Dinâmicos (03/06/2026)

- [x] 3 categorias por dias de atraso: Novos (1d) · Régua (2–29d) · Acima 30 Dias (30d+)
- [x] Cards de filtro clicáveis em Resultado (JS filtra + atualiza totalizadores)
- [x] Migração automática de estado pickle com categorias antigas (A/B)

---

## ✅ FASE D — Multi-empresa (03/06/2026)

- [x] Toggle `[Ineprotec | Mat. EaD]` na topbar
- [x] PK composta `(cpf, empresa)` na tabela `inadimplentes`
- [x] Templates padrão duplicados por empresa
- [x] Uploads e relatórios separados por empresa
- [x] Migração automática: dados existentes preservados como INEPROTEC

---

## ✅ FASE E — Régua de Cobranças + Arquivo À Vencer (04/06/2026)

- [x] Processamento do arquivo AVENCER — card laranja + tabela "A Vencer" em Resultado
- [x] Placeholder `{LINK_PAGAMENTO}` nos templates (preenchimento manual no TXT)
- [x] Campo `qtd_cobranca` no banco — incrementa a cada relatório gerado
- [x] Coluna "Cobr." na tela Base
- [x] Nova aba "Régua" em Configurações
- [x] Estrutura `C:\MATINE\` criada automaticamente no startup
- [x] Submenu de Configurações na sidebar

---

## ✅ FASE F — Wizard de Envio WhatsApp (04/06/2026)

- [x] Tela `/envio-mensagens` com todas as mensagens formatadas
- [x] Botão "Copiar" por linha + expansão inline da mensagem
- [x] Barra de progresso: X/Y enviados + percentual
- [x] Marcar enviado por aluno (AJAX, sem reload)
- [x] Botão "Marcar Todos Enviados"
- [x] Tabela `envios` no banco (base para rastreamento por canal)
- [x] Filtro por categoria + busca por nome/telefone + ocultar enviados

---

## ✅ FASE G — Cobranças por E-mail (04/06/2026)

- [x] Configuração SMTP por empresa (host, port, usuário, senha, TLS)
- [x] Teste de conexão SMTP na tela de Configurações
- [x] Envio individual por aluno (AJAX)
- [x] Envio em lote para todos com e-mail cadastrado
- [x] Campo `assunto_email` nos templates
- [x] Registro de envios na tabela `envios` (canal='email')

---

## ✅ MUDANÇAS 1–5 — UX e CRM (08/06/2026)

- [x] Aba Resultado: removidos 4 botões redundantes (mantém só "Gerar Relatórios")
- [x] Após gerar relatório → redireciona para `/resultado` (não mais para envio de mensagens)
- [x] `wizard_whatsapp` renomeado para `envio_mensagens` em todo o código
- [x] Campo `tag_crm` nos templates + botão "Planilha CRM" em Envio de Mensagens
- [x] Aba Base: 4 cards de filtro rápido com lógica correta:
  - Novos Inadimplentes (`categoria = 'Novos Inadimplentes'`)
  - Em Renegociação (CPF presente no arquivo À Vencer da sessão)
  - Inadimplentes Gerais (`status = INADIMPLENTE` e não é Novo)
  - Inadimplentes Quitados (`status = QUITADO`)

---

## ✅ CORREÇÕES DE UI — Resultados + Base (10/06/2026)

Ajustes reportados pelo Edilvo na revisão do app. Apenas template + JS, sem backend.

- [x] **R1** — Cards "Vence Hoje" / "À Vencer" (Resultados) com auto-filtro, igual aos demais cards. Filtro estendido para a tabela "A Vencer" separada, com toggle de seção.
- [x] **R2** — Dropdown Filtrar de Resultados com as 5 categorias (Vence Hoje + A Vencer incluídas).
- [x] **B1** — Removidas as legendas INADIMPLENTE / QUITADO / RENEGOCIADO da aba Base.
- [x] **B2** — Dropdown Filtrar da Base com 5 categorias; "Vence Hoje"/"A Vencer" filtram pelas flags de sessão À Vencer.

---

## ✅ STORY-01-01 — Quick Wins (10/06/2026)

Primeira story do EPIC-01 entregue. 2 dos 5 itens já estavam satisfeitos pelo estado do app.

- [x] Encoding UTF-8 sem BOM (já OK em todos os templates)
- [x] Cores semânticas por categoria em Resultado e Envio de Mensagens (já OK)
- [x] Título dinâmico por página via `{% block title %}` (layout + 5 templates)
- [x] Confirmação modal antes de "Limpar Sessão" (não afeta a Base)
- [x] `secret_key` Flask gerada uma vez e persistida em `.env` (gitignored, sem dependência nova)

---

## ✅ STORY-01-02 — Indicadores de Empresa Ativa (10/06/2026)

- [x] Nome da empresa colorido na topbar (azul Ineprotec · verde Mat. EaD), acima do toggle
- [x] Banner "Enviando para: [EMPRESA]" no topo do wizard de envio
- [x] Confirmação ao trocar de empresa quando há consolidação ativa (flag `sessao_ativa`)

---

## ✅ STORY-01-03 — Loading States e Confirmação Atualizar Base (10/06/2026)

- [x] Handler global reutilizável em `layout.html`: todo `<form data-loading>` desabilita o botão de submit e troca o texto por spinner (`data-loading-text`), impedindo duplo clique
- [x] Loading state aplicado a: Consolidar, Gerar Relatórios (Início + Resultado), Atualizar Base, Importar Alunos, Salvar SMTP, Testar Conexão SMTP
- [x] Modal de confirmação antes de "Comparar e Atualizar Base" (`#modalAtualizarBase`, padrão consistente com Limpar Sessão/Limpar Base)
- [x] Flash de `/gerar-relatorio` com contagem total: "X mensagens prontas para envio"

---

## ✅ STORY-01-05 — Schema Migrations + Índices + WAL (10/06/2026)

Fundação de versionamento de banco — maior bloqueador técnico para a Fase H.

- [x] Tabela `schema_migrations` (version, name, applied_at)
- [x] `init_db()` refatorado de 163 linhas com 7 fases inline → runner que aplica só migrations pendentes
- [x] Diretório `06_APP/migrations/` com `runner.py` + scripts 001–006 (cada um com `up`/`down`)
- [x] Migrations atômicas (BEGIN/COMMIT por script); WAL como migration não-transacional
- [x] 5 índices de performance por `empresa` (migration 005)
- [x] WAL mode + `foreign_keys=ON` em `get_conn()` (leituras concorrentes — necessário p/ Fase H)
- [x] Detecção de banco legado: 001–004 marcadas como aplicadas sem re-executar
- [x] Banco real de produção migrado sem perda de dados (1024 inadimplentes; backup criado)

---

## ✅ STORY-01-04 — Senha SMTP Segura (keyring) (10/06/2026)

Senha SMTP fora do banco — fecha exposição em backups/cópias do `inadimplencia.db`.

- [x] `keyring>=25.0.0` (backend WinVaultKeyring = Windows Credential Manager)
- [x] `salvar_config_email` grava no keyring; coluna `smtp_senha` guarda só `[keyring]`
- [x] `get_config_email` lê do keyring (fallback: env `SMTP_<EMPRESA>_SENHA` → coluna legado)
- [x] Migração de segurança no startup: senha em texto plano → keyring (banco real migrado)
- [x] UI não vaza a senha no HTML; bullets quando configurada; campo vazio preserva a atual
- [x] Caminho de envio/teste SMTP inalterado (consome `config['smtp_senha']`)

---

## ✅ STORY-01-06 — Autenticação Flask-Login (10/06/2026)

Fecha o vetor de acesso aberto — pré-requisito de segurança para a Fase H (webhooks).

- [x] `flask-login>=0.6.3` + usuário único via `.env` (`APP_USUARIO`/`APP_SENHA`)
- [x] Senha como hash pbkdf2 (`werkzeug.security`) — nunca em texto plano
- [x] Login/logout funcionais; `remember=True` com cookie de 7 dias
- [x] Proteção de todas as rotas via guard global `before_request` (default-deny; allowlist login/logout/static) — novas rotas já nascem protegidas
- [x] Tela `login.html` standalone (logos, centralizada, sem sidebar) + footer da sidebar com usuário e botão Sair
- [x] Seed de fábrica `luana` / `matine2026` na 1ª execução (troca via `.env.example`)
- [x] Smoke test (Flask test client): 8/8 PASS, incluindo bloqueio de open-redirect

---

## 🔲 EPIC-01 — Sprint Zero (Pré-Fase H)

Resolução de débitos técnicos críticos identificados no Brownfield Discovery.
**Pré-requisito para Fase H.** Ver detalhes em `PLANO_DE_ACAO.md`.

| Story | Título | Esforço | Status |
|-------|--------|---------|--------|
| 01-01 | Quick Wins — encoding, cores, títulos, confirmações, secret key | ~7h | ✅ 10/06 |
| 01-02 | Indicadores de empresa ativa (topbar + wizard) | ~3h | ✅ 10/06 |
| 01-03 | Loading states + confirmação "Atualizar Base" | ~5h | ✅ 10/06 |
| 01-04 | Proteger senha SMTP com Python Keyring | ~4h | ✅ 10/06 |
| 01-05 | Schema migrations + índices + WAL mode | ~12h | ✅ 10/06 |
| 01-06 | Autenticação Flask-Login (MVP) | ~6h | ✅ 10/06 |
| 01-07 | First-run setup robusto (estrutura `C:\MATINE` + onboarding dev) | ~3h | Pendente |

---

## 🔲 FASE H — Integrações Automáticas (após EPIC-01)

- [ ] WhatsApp automático via WAHA / Evolution API / Z-API / Twilio
- [ ] Link de pagamento dinâmico por aluno (API Synapta — substitui `{LINK_PAGAMENTO}`)
- [ ] Kommo CRM — tagging automático via API (add/remove tag INADIMPLENTE)
- [ ] Agendamento diário/semanal de cobranças

---

## 💡 INSIGHTS — Próxima Versão

Observações e aprendizados do uso real. Serão tratados após Fase H como backlog da v2.

### Operação

- **Separação automática Quitado × Renegociado:** Hoje é revisão manual (coluna `Situacao` em branco no XLSX). A distinção automática exige rastrear se o CPF saiu dos vencidos e apareceu no À Vencer — o arquivo Synapta mistura os dois casos. Solução robusta requer lógica de estado por CPF com janela temporal.

- **Alunos sem telefone:** ~252 alunos sem telefone na base. O aviso de "sem cadastro" existe, mas não há fluxo para enriquecer o cadastro dentro do app. Considerar tela de enriquecimento manual ou integração com Synapta.

- **Heurística de gênero frágil:** Nomes terminados em "a" → sra. Falha em nomes como "Joshua", "Elias", "Matias". Melhorar com lista de exceções ou biblioteca de classificação de nomes.

### Produto

- **Dashboard analítico:** Qtd e valor de inadimplentes por período, evolução de quitações, taxa de resposta ao WhatsApp. Hoje não existe nenhuma visão histórica no app.

- **Régua configurável por aluno:** Hoje a régua é por categoria (dias de atraso). Ideal seria configurar frequência por aluno (ex.: cliente preferencial com régua mais suave).

- **Negativação automática:** Estava no plano original. Clientes acima de 30 dias sem resposta entrariam em fluxo de negativação. Requer conformidade legal e parceiro de negativação (Serasa, SPC).

- **Multi-usuário:** Hoje o app é mono-usuário (Flask-Login MVP com usuário único). Com crescimento da equipe de cobranças, precisará de usuários por empresa com permissões distintas.

### Técnico

- **Arquivo Synapta sem CPF:** Quando o arquivo À Vencer não tem CPF, o cruzamento é feito por nome (match aproximado). Erros de grafia resultam em CPF vazio e o aluno não é reconhecido como "Em Renegociação". Solução: solicitar ao Synapta exportação com CPF ou implementar fuzzy matching.

- **Pickle de sessão sem expiração:** O estado de consolidação fica em pickle indefinidamente. Se o arquivo fonte mudar sem nova consolidação, os dados exibidos ficam desatualizados silenciosamente. Considerar timestamp de validade ou aviso visual de sessão antiga.

- **Relatórios acumulam sem limpeza:** A pasta `C:\MATINE\relatorios\` cresce indefinidamente. Implementar política de retenção (ex.: 90 dias) ou tela de gerenciamento.
