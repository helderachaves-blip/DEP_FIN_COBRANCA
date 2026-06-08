# EPIC-01: Sprint Zero — Pre-Fase H
## Resolucao de Debitos Criticos e Desbloqueio da Fase H

**Epic ID:** EPIC-01
**Status:** Ready
**PM:** Morgan (@pm)
**Prioridade:** P0 — Pre-requisito para qualquer nova funcionalidade
**Estimativa:** ~34h (~4 semanas)
**Criado em:** 04/06/2026
**Fonte:** Brownfield Discovery — docs/prd/technical-debt-assessment.md

---

## Objetivo do Epic

Resolver os 10 debitos criticos identificados no Brownfield Discovery, com foco em:
1. Eliminar riscos de seguranca ativos (senhas expostas, sem autenticacao)
2. Prevenir perda de dados por operacao incorreta (acoes sem confirmacao)
3. Desbloquear a Fase H (WhatsApp automatico + Kommo CRM)
4. Melhorar a experiencia diaria da Luana (loading screens, indicadores visuais)

---

## Stories do Epic

| Story | Titulo | Esforco | Prioridade | Status |
|-------|--------|---------|-----------|--------|
| STORY-01-01 | Quick Wins — Encoding, Cores, Titulos e Confirmacoes | ~7h | P1 | Draft |
| STORY-01-02 | Indicadores de Empresa Ativa (topbar + wizard) | ~3h | P1 | Draft |
| STORY-01-03 | Loading States em Acoes Sincronas | ~3h | P1 | Draft |
| STORY-01-04 | Proteger Senha SMTP com Python Keyring | ~4h | P1 | Draft |
| STORY-01-05 | Schema Migrations + Indices + WAL Mode | ~12h | P1 | Draft |
| STORY-01-06 | Autenticacao Flask-Login (MVP) | ~6h | P1 | Draft |

**Total estimado: ~35h**

---

## Dependencias entre Stories

```
STORY-01-01 → independente (pode comecar imediatamente)
STORY-01-02 → independente
STORY-01-03 → independente
STORY-01-04 → independente
STORY-01-05 → independente (mas DEVE preceder qualquer outro debito de banco)
STORY-01-06 → independente (pode ser desenvolvida em paralelo)
```

---

## Criterios de Conclusao do Epic

- [ ] Todos os 10 debitos criticos marcados como resolvidos
- [ ] Nenhum dado sensivel armazenado em texto plano
- [ ] Todas as acoes destrutivas protegidas com confirmacao
- [ ] Sistema com autenticacao funcional (mesmo que usuario unico)
- [ ] Banco de dados com schema_migrations implementado
- [ ] Indicadores de empresa ativa visiveis em todas as telas de risco
- [ ] QA Quinn executou smoke test no fluxo completo (Upload → Consolidar → Envio de Mensagens)

---

## Definicao de Pronto (DoD) do Epic

- Todas as stories com status Done
- Sem regressoes no fluxo principal (Upload, Consolidar, Gerar, Envio de Mensagens)
- Commit com referencia ao epic: `feat: [EPIC-01] ...`
- Documentacao de operacao atualizada (README ou guia de uso)

---

*Morgan (@pm) — Brownfield Discovery Fase 10 — MAT-INE Inadimplencia 2026*
