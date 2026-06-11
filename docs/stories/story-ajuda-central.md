# STORY-AJUDA: Central de Ajuda
**Epic:** Suporte & UX (pós-EPIC-01)
**Status:** Done (10/06/2026)
**Esforco estimado:** ~2h
**Prioridade:** P2

---

## Contexto

A operadora (Luana) e nao tecnica e depende de Edilvo/Helder para tirar duvidas de uso.
Uma Central de Ajuda dentro do proprio sistema, explicando cada tela em linguagem simples,
reduz essa dependencia e serve de onboarding para novos operadores.

**Decisao (alinhada com Helder):**
- Formato: **pagina com indice lateral** (estilo documentacao) — `/ajuda` no menu lateral.
- Conteudo: **operacional, passo a passo**, focado na operadora (sem detalhes tecnicos
  de SMTP/banco).

---

## Acceptance Criteria

- [x] Rota `/ajuda` (protegida pelo login, como as demais — guard global `before_request`)
- [x] Link "Ajuda" na barra lateral (secao Suporte)
- [x] Template `ajuda.html` com indice lateral fixo (sticky) + conteudo por tela
- [x] Realce da secao ativa ao rolar (Bootstrap ScrollSpy; degrada sem quebrar)
- [x] Seccoes cobrindo todas as telas: Visao geral, Inicio, Resultado, Envio de Mensagens,
      Base, Configuracoes + Duvidas frequentes
- [x] Linguagem operacional passo a passo (o que clicar e em que ordem), com dicas e avisos
- [x] Responsivo: o indice lateral some em telas estreitas (conteudo continua acessivel)

## Arquivos Criados / Modificados

- `06_APP/app.py` — rota `/ajuda` (render de `ajuda.html`)
- `06_APP/templates/ajuda.html` — **novo** (indice lateral + 7 secoes + ScrollSpy)
- `06_APP/templates/layout.html` — link "Ajuda" na sidebar (secao Suporte)

## Conteudo das telas documentado

Visao geral (login, troca de empresa, sair) · Inicio (importar + consolidar) ·
Resultado (cartoes-filtro, busca, gerar relatorios) · Envio de Mensagens (WhatsApp copiar/marcar,
e-mail, filtros, planilha CRM) · Base (status, atualizar base, limpar) ·
Configuracoes (Mensagens/Regua/Clientes/E-mail/Zona de Risco) · Duvidas frequentes.

## Testes executados (10/06/2026)

Todos PASS: `/ajuda` sem login redireciona; com login 200; pagina contem titulo, as 5 secoes
de tela e o link da sidebar; `py_compile` OK.

## Manutencao

O conteudo e estatico no template `ajuda.html`. Ao mudar/adicionar uma tela, atualizar a
secao correspondente e, se for nova tela, acrescentar um item no indice lateral (`#ajuda-nav`)
e a `<section>` com o mesmo `id`.

## Change Log

| Data | Status | Autor | Nota |
|------|--------|-------|------|
| 10/06/2026 | Draft -> Done | @dev | Central de Ajuda com indice lateral, conteudo operacional. |

---
*STORY-AJUDA — Suporte & UX — MAT-INE Inadimplencia 2026*
