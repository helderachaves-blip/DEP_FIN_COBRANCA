# STORY-H-02 — Dashboard Analítico Básico

**Epic:** Fase H — Integrações · Sprint H-2
**Status:** InProgress
**Branch:** `homologacao`

---

## Contexto

O Sprint H-2 originalmente previa dois itens: *Agendamento via Windows Task Scheduler*
e *Dashboard analítico*. Com o EPIC-02 (app no Render/Linux, stateless), o agendamento
via Task Scheduler ficou obsoleto — e, sem ingestão automática do Synapta, não há fonte
para "consolidar automaticamente". **Decisão (17/06/2026):** o agendamento sai do H-2
(os jobs de infra que realmente importam — dump do Postgres e keep-alive — viram backlog
de infra do EPIC-02/v2). O H-2 fica focado no **Dashboard**.

## Objetivo

Dar ao gestor (Edilvo) uma visão analítica da carteira de inadimplência, por empresa
ativa, **usando apenas os dados que o app já registra** (`inadimplentes`,
`historico_atualizacoes`, `envios`). Sem novas tabelas, sem novas dependências de backend.

## Acceptance Criteria

- **AC-1** — Rota `/dashboard` protegida pelo login, escopada pela empresa ativa (toggle da topbar).
- **AC-2** — KPIs no topo: total de inadimplentes, valor em aberto (R$), quitados,
  em renegociação, mensagens enviadas no período.
- **AC-3** — Gráfico de **evolução da carteira** (total da base por semana ISO), a partir
  de `historico_atualizacoes`.
- **AC-4** — **Distribuição por categoria** (Novos / Régua / Acima 30 dias) dos inadimplentes
  ativos — quantidade e valor.
- **AC-5** — **Taxa de quitação pós-cobrança**: dos CPFs com `qtd_cobranca>0`, % que hoje
  estão `QUITADO`. Mostra também o numerador/denominador para leitura honesta.
- **AC-6** — Estado vazio amigável quando ainda não há dados (link para Início).
- **AC-7** — Cross-dialect (SQLite + Postgres): agregação por data feita em Python sobre
  texto pt-BR (`dd/mm/AAAA`), sem funções de data específicas de dialeto.
- **AC-8** — Link "Dashboard" na sidebar.

## Notas de implementação

- `db.dashboard_stats(empresa, dias=30)` concentra a agregação. Counts/somas via SQL
  (cross-dialect), recortes por data em Python (`_parse_dt_br`).
- Gráficos via **Chart.js** (CDN, só no template do dashboard) — coerente com o padrão
  de carregar Bootstrap/ícones por CDN.
- Evolução bucketizada por semana ISO: dentro da semana soma novos/saídos e mantém o
  último `total_base`; série limitada às últimas 12 semanas.

## File List

- `06_APP/database.py` — `_parse_dt_br`, `dashboard_stats`
- `06_APP/app.py` — rota `/dashboard`
- `06_APP/templates/dashboard.html` — novo
- `06_APP/templates/layout.html` — link na sidebar
- `06_APP/tests/test_dashboard.py` — novo

## Fora de escopo (v.next)

- Taxa de resposta ao WhatsApp / conversões reais (exigiria callback do Kommo).
- Filtro de período interativo no front (entrega inicial usa janela fixa de 30 dias p/ envios).
- Agendamento de jobs (movido para backlog de infra do EPIC-02/v2).
