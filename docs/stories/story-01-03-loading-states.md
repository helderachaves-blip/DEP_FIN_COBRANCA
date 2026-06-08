# STORY-01-03: Loading States e Confirmacao do Atualizar Base
**Epic:** EPIC-01 Sprint Zero
**Status:** Draft
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

- [ ] **Botao "Consolidar Agora"** em `index.html`: desabilitado + spinner durante POST /consolidar
- [ ] **Botao "Gerar Relatorios WhatsApp"** em `index.html` e `resultado.html`: desabilitado + spinner durante POST /gerar-relatorio
- [ ] **Botao "Comparar e Atualizar Base"** em `index.html` e `resultado.html`: desabilitado + spinner durante POST /atualizar-base
- [ ] **Botao "Importar Alunos"** em `configuracoes.html`: desabilitado + spinner durante POST /upload-alunos
- [ ] **Botao "Salvar Configuracoes SMTP"** em `configuracoes.html`: desabilitado + spinner
- [ ] **Botao "Testar Conexao SMTP"** em `configuracoes.html`: desabilitado + spinner
- [ ] Texto do spinner e contextual: "Consolidando...", "Gerando Relatorios...", "Atualizando Base...", etc.

### AC-02 — Confirmacao no "Comparar e Atualizar Base" (UX-CRIT-02)
- [ ] Modal Bootstrap exibido antes de executar POST /atualizar-base
- [ ] Modal informa: "Esta acao atualizara permanentemente a base de [EMPRESA] com os dados importados. Deseja continuar?"
- [ ] Dois botoes: "Cancelar" (fecha modal) e "Atualizar Base" (dispara o form)
- [ ] Loading state (AC-01) se aplica ao botao de confirmacao dentro do modal
- [ ] Consistente com o padrao do modal "Limpar Base" ja existente em Configuracoes

### AC-03 — Flash message explicita apos "Gerar Relatorios" (UX-HIGH-06)
- [ ] Rota `/gerar-relatorio` retorna flash message informativa: "Relatorios gerados com sucesso para [EMPRESA]. X mensagens prontas para envio."
- [ ] Flash aparece na pagina de destino (/wizard-whatsapp) com categoria "success"

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

*STORY-01-03 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
