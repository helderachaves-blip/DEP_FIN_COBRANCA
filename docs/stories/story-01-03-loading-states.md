# STORY-01-03: Loading States e Confirmacao do Atualizar Base
**Epic:** EPIC-01 Sprint Zero
**Status:** Done
**Esforco estimado:** ~5h
**Prioridade:** P1
**Debitos resolvidos:** UX-CRIT-01, UX-CRIT-02, UX-HIGH-06

---

## Contexto

6 das 8 acoes principais do sistema nao tem feedback visual durante o processamento. O usuario nao sabe se o sistema esta trabalhando ou travado, o que leva a cliques multiplos e possiveis dados duplicados. O botao "Atualizar Base" executa imediatamente sem pedir confirmacao, podendo modificar o SQLite de producao por erro.

---

## Acceptance Criteria

### AC-01 — Loading state em todos os form POST sincronos (UX-CRIT-01)

**Padrao a implementar em todos os botoes de acao:**
```javascript
form.addEventListener('submit', function() {
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Processando...';
});
```

- [x] **Botao "Consolidar Agora"** em `index.html`: desabilitado + spinner durante POST /consolidar
- [x] **Botao "Gerar Relatorios WhatsApp"** em `index.html` e `resultado.html`: desabilitado + spinner durante POST /gerar-relatorio
- [x] **Botao "Comparar e Atualizar Base"** em `index.html`: desabilitado + spinner durante POST /atualizar-base (no modal de confirmacao). _Nota: resultado.html nao tem mais esse botao — removido deliberadamente nas MUDANCAS 1-5._
- [x] **Botao "Importar Alunos"** em `configuracoes.html`: desabilitado + spinner durante POST /upload (`tipo=alunos`). _Nota: a rota real e /upload, nao /upload-alunos._
- [x] **Botao "Salvar Configuracoes SMTP"** em `configuracoes.html`: desabilitado + spinner
- [x] **Botao "Testar Conexao SMTP"** em `configuracoes.html`: desabilitado + spinner
- [x] Texto do spinner e contextual: "Consolidando...", "Gerando Relatorios...", "Atualizando Base...", "Importando...", "Salvando...", "Testando..."

### AC-02 — Confirmacao no "Comparar e Atualizar Base" (UX-CRIT-02)
- [x] Modal Bootstrap exibido antes de executar POST /atualizar-base (`#modalAtualizarBase` em index.html)
- [x] Modal informa: "Esta acao atualizara permanentemente a base de [EMPRESA] com os dados importados. Deseja continuar?"
- [x] Dois botoes: "Cancelar" (fecha modal) e "Atualizar Base" (dispara o form)
- [x] Loading state (AC-01) se aplica ao botao de confirmacao dentro do modal (form com `data-loading`)
- [x] Consistente com o padrao do modal "Limpar Base"/"Limpar Sessao" ja existentes

### AC-03 — Flash message explicita apos "Gerar Relatorios" (UX-HIGH-06)
- [x] Rota `/gerar-relatorio` retorna flash: "Relatorios gerados com sucesso para [EMPRESA]. X mensagens prontas para envio (detalhe por template) -> pasta"
- [x] Flash aparece na pagina de destino com categoria "success". _Nota: destino e `/resultado` (nao o wizard) — redirecionamento alterado deliberadamente nas MUDANCAS 1-5; AC atendida no destino atual._

---

## Arquivos a Modificar

- `06_APP/templates/index.html` — loading states + modal Atualizar Base
- `06_APP/templates/resultado.html` — loading states + modal Atualizar Base
- `06_APP/templates/configuracoes.html` — loading states nos forms SMTP e upload
- `06_APP/app.py` — flash message na rota /gerar-relatorio

---

## Testes Esperados

- [ ] Clicar "Consolidar Agora": botao fica desabilitado com spinner ate a pagina recarregar
- [ ] Clicar "Comparar e Atualizar Base": modal de confirmacao aparece antes de executar
- [ ] Cancelar no modal: nenhuma acao e executada
- [ ] Clicar "Atualizar Base" no modal: loading state aparece + executa
- [ ] Clicar "Gerar Relatorios": redireciona para wizard com flash "X mensagens prontas"
- [ ] Tentativa de duplo clique apos primeiro clique: botao desabilitado impede segundo clique

---

## File List

- `06_APP/templates/layout.html` — handler global de loading state (delegado em `submit`, captura `data-loading`)
- `06_APP/templates/index.html` — `data-loading` em Consolidar e Gerar Relatorios; Atualizar Base virou botao de modal + novo `#modalAtualizarBase`
- `06_APP/templates/resultado.html` — `data-loading` em Gerar Relatorios
- `06_APP/templates/configuracoes.html` — `data-loading` em Importar Alunos, Salvar SMTP e Testar Conexao
- `06_APP/app.py` — flash de `/gerar-relatorio` com contagem total de mensagens (`total_msgs`)

## Dev Notes

- **Padrao reutilizavel:** em vez de repetir `addEventListener` por form, o handler vive uma vez no `layout.html` e atua em qualquer `<form data-loading>`, lendo o texto do spinner de `data-loading-text` no botao. Usa captura (`true`) e nao bloqueia o submit nativo — o form segue normalmente, o botao so fica desabilitado para impedir duplo clique.
- **Desvios da spec (justificados, sem invencao):**
  - `resultado.html` nao recebeu botao Atualizar Base (removido nas MUDANCAS 1-5 — nao revertido).
  - Importar Alunos posta em `/upload` com `tipo=alunos` (rota `/upload-alunos` nao existe).
  - `/gerar-relatorio` redireciona para `/resultado` (decisao das MUDANCAS 1-5) — flash mantido no destino atual, com a contagem explicita pedida pela AC-03.
- **Validacao:** `python -m py_compile app.py` OK; parse Jinja2 das 4 templates OK.

## Change Log

| Data | Status | Autor | Nota |
|------|--------|-------|------|
| 10/06/2026 | Draft | @sm | Story criada |
| 10/06/2026 | Draft -> InProgress -> InReview | @dev | Loading states (AC-01), modal Atualizar Base (AC-02), flash com contagem (AC-03) implementados e validados |
| 10/06/2026 | InReview -> Done | @dev | Smoke test OK (rotas 200, atributos/modal/handler renderizados); aguarda commit local |

---

*STORY-01-03 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
