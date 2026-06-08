# Roadmap de Ajustes — Consolidador Web MAT-INE

> Histórico de entregas e próximas fases.
> ✅ = concluído · 🔲 = pendente

---

## ✅ FASE A — UX Rápidos (03/06/2026)

- [x] Alinhamento `text-end` + `text-nowrap` nas colunas de valores
- [x] Mover importação de Alunos para Configurações
- [x] Botão "Limpar Base" com modal de confirmação (digitar "LIMPAR")
- [x] Aviso de alunos sem cadastro após consolidação (flash warning)
- [x] Pastas de mês com nome por extenso: `01-Janeiro` … `12-Dezembro`

---

## ✅ FASE B — Redesign Layout Sidebar (03/06/2026)

- [x] Sidebar escura (`#1a1a2e`) substituindo navbar horizontal
- [x] "Cobranças INE-MAT" no topo da sidebar
- [x] Topbar mesma cor com logos Ineprotec (esq) e Matrícula EaD (dir) — RGBA transparente

---

## ✅ FASE C — Reformulação das Categorias + Filtros Dinâmicos (03/06/2026)

- [x] 3 categorias por dias de atraso: Novos Inadimplentes (1d) · Régua (2-29d) · Acima 30 Dias (30d+)
- [x] Cards de filtro clicáveis em Resultado (JS filtra tabela + atualiza totalizadores)
- [x] Totalizadores dinâmicos: "Total de Inadimplentes" e "Total em Atraso"
- [x] Migração automática de estado pickle com categorias antigas (A/B)

---

## ✅ FASE D — Multi-empresa (03/06/2026)

- [x] Toggle `[Ineprotec | Mat. EaD]` na topbar
- [x] Tabela `inadimplentes` recriada com PK composta `(cpf, empresa)`
- [x] Colunas `empresa` adicionadas em `templates` e `historico_atualizacoes`
- [x] Migração automática: dados existentes preservados como `INEPROTEC`
- [x] Templates padrão duplicados por empresa
- [x] Pastas separadas para uploads e relatórios por empresa

---

## ✅ FASE E — Régua de Cobranças + Padrão de Projeto (04/06/2026)

- [x] Processamento do arquivo AVENCER — card laranja + tabela "A Vencer" em Resultado
- [x] Placeholder `{LINK_PAGAMENTO}` nos templates (mantido no TXT para preenchimento manual)
- [x] Campo `qtd_cobranca` no banco — incrementa a cada relatório gerado
- [x] Coluna "Cobr." na tela Base
- [x] Nova aba "Régua" em Configurações (tabs: Mensagens / Régua / Alunos / Zona de Risco)
- [x] **Padrão de estrutura em `C:\MATINE\`** — criada automaticamente no startup
  - `uploads/{EMPRESA}/{tipo}/` — detecção por pasta, nome livre
  - `relatorios/{EMPRESA}/{ano}/{mes}/{dia}/` — relatórios datados
  - `banco/inadimplencia.db` · `estado/` · `logs/`
- [x] **Submenu de Configurações na sidebar** — Mensagens · Régua · Alunos · Zona de Risco

---

## ✅ FASE F — Wizard de Envio WhatsApp (04/06/2026)

- [x] Tela `/wizard-whatsapp` — aberta automaticamente após gerar relatório
- [x] Tabela com todas as mensagens formatadas por aluno + botão "Copiar" por linha
- [x] Expansão por clique: mostra mensagem inline + botão "Copiar Mensagem"
- [x] Barra de progresso: X/Y enviados + percentual
- [x] Marcar enviado por aluno (AJAX, sem reload de página)
- [x] Botão "Marcar Todos Enviados"
- [x] Tabela `envios` no banco — rastreia envios por canal/dia/empresa (base Fase H)
- [x] Filtro por categoria + busca por nome/telefone + ocultar enviados
- [x] Link "Wizard de Envio" na sidebar + botão na tela Resultado

**Arquivos alterados:**
- `06_APP/app.py` — rotas `/wizard-whatsapp`, `/whatsapp/marcar-enviado`, `/whatsapp/marcar-todos`
- `06_APP/database.py` — tabela `envios`, funções `registrar_envio()`, `get_envios_hoje()`
- `06_APP/templates/wizard_whatsapp.html` — nova tela
- `06_APP/templates/resultado.html` — botão "Wizard de Envio"
- `06_APP/templates/layout.html` — link na sidebar

---

## ✅ FASE G — Cobranças por E-mail (04/06/2026)

- [x] Configuração SMTP por empresa (host, port, usuário, senha, from_name, TLS)
- [x] Teste de conexão SMTP na tela de Configurações
- [x] Envio de e-mail individual por aluno (AJAX no Wizard de Envio)
- [x] Envio em lote para todos com e-mail cadastrado (sessão SMTP única)
- [x] Coluna `assunto_email` nos templates — assunto configurável por mensagem
- [x] Fallback de assunto padrão por categoria
- [x] Registro de todos os envios na tabela `envios` (canal='email')
- [x] Aba "E-mail" em Configurações — SMTP + assuntos por template
- [x] Botão "Enviar E-mail" por aluno no Wizard (apenas se tem e-mail cadastrado)
- [x] Botão "Enviar E-mail para Todos" no Wizard

**Arquivos alterados:**
- `06_APP/app.py` — rotas `/email/configurar`, `/email/testar`, `/email/enviar-aluno`, `/email/enviar-todos`, `/email/assunto/<tid>`
- `06_APP/database.py` — tabela `config_email`, funções `salvar_config_email()`, `get_config_email()`, `salvar_assunto_template()`
- `06_APP/templates/configuracoes.html` — aba E-mail
- `06_APP/templates/layout.html` — sublink E-mail na sidebar

---

## 🔲 FASE H — Integrações Automáticas *(depende de F e G)*

- [ ] WhatsApp automático via WAHA/Twilio
- [ ] Link de pagamento Synapta dinâmico por aluno (substitui `{LINK_PAGAMENTO}`)
- [ ] Kommo CRM — tagging automático
- [ ] Agendamento diário/semanal
