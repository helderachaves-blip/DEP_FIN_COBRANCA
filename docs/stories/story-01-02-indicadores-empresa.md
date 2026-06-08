# STORY-01-02: Indicadores de Empresa Ativa
**Epic:** EPIC-01 Sprint Zero
**Status:** Draft
**Esforco estimado:** ~3h
**Prioridade:** P1
**Debitos resolvidos:** UX-NEW-01, UX-LOW-04

---

## Contexto

O maior risco operacional diario e a Luana enviar cobrancas para clientes da empresa errada. O indicador atual — opacidade do logo no toggle — e sutil demais. Este story adiciona indicadores persistentes e nao ambiguos da empresa ativa.

---

## Acceptance Criteria

### AC-01 — Nome da empresa em texto na topbar (UX-LOW-04)
- [ ] Topbar exibe o nome da empresa ativa em texto ao lado do toggle: "INEPROTEC" ou "MATRICULAEAD"
- [ ] Nome usa cor de destaque por empresa: azul (#1565C0) para Ineprotec, verde (#2e7d32) para Matricula EAD
- [ ] Texto visivel em todas as paginas (via layout.html)

### AC-02 — Banner de contexto no wizard de Envio de Mensagens (UX-NEW-01)
- [ ] `wizard_whatsapp.html` exibe banner persistente no topo do conteudo (abaixo do cabecalho)
- [ ] Banner mostra: "Enviando para: [NOME DA EMPRESA]" com fundo colorido por empresa
- [ ] Banner nao pode ser fechado (e um lembrete permanente, nao um alerta dismissivel)
- [ ] Cor do banner: azul para Ineprotec, verde para Matricula EAD

### AC-03 — Confirmacao na troca de empresa com sessao ativa (bonus)
- [ ] Se existir pickle de consolidacao carregado, exibir `confirm("Voce esta trocando para [empresa]. Os dados consolidados de [empresa atual] nao serao perdidos. Continuar?")` antes de executar a troca
- [ ] Troca sem sessao ativa: executa imediatamente (comportamento atual mantido)

---

## Arquivos a Modificar

- `06_APP/templates/layout.html` — nome da empresa na topbar
- `06_APP/templates/wizard_whatsapp.html` — banner de empresa
- `06_APP/app.py` — garantir que `empresa_ativa` esta disponivel no context global do Jinja2

---

## Testes Esperados

- [ ] Selecionar INEPROTEC: topbar e banner do wizard mostram "INEPROTEC" em azul
- [ ] Selecionar MATRICULAEAD: topbar e banner mostram "MATRICULAEAD" em verde
- [ ] Abrir o wizard sem consolidacao: banner ainda aparece com empresa ativa
- [ ] Trocar empresa com sessao ativa: dialogo de confirmacao aparece

---

*STORY-01-02 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
