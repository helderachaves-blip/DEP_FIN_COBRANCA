# UX Specialist Review
**Revisor:** @ux-design-expert (Uma)
**Data:** 04/06/2026
**DRAFT revisado:** docs/prd/technical-debt-DRAFT.md (Secao 4)
**Base:** frontend-spec.md (Fase 3) + releitura direta dos 6 templates em 06_APP/templates/

---

## 1. Debitos Validados

| ID | Debito | Sev. Original | Sev. Revisada | Horas Est. (revisadas) | Prioridade | Notas |
|----|--------|---------------|---------------|------------------------|------------|-------|
| UX-CRIT-01 | Ausencia total de loading state em acoes sincronas longas (Consolidar, Gerar Relatorios, Atualizar Base, Upload) | CRITICO | CRITICO | 3h | P1 | Estimativa original de 4h revisada para 3h. Todos os form POST sincronos: padrao unico — desabilitar btn no submit + spinner inline. Implementacao em index.html cobre os 4 botoes de uma vez. |
| UX-CRIT-02 | Comparar e Atualizar Base executa imediatamente sem confirmacao — acao modifica SQLite permanentemente | CRITICO | CRITICO | 2h | P1 | Confirmado. Botao btn-warning sem modal nem confirm(). Contraste grave com Limpar Base que tem modal + digitacao LIMPAR. 2h inclui modal Bootstrap + ajuste dos dois locais (index.html e resultado.html). |
| UX-CRIT-03 | Limpar Sessao executa como link GET sem confirmacao — perda total da consolidacao por clique acidental | CRITICO | CRITICO | 1h | P1 | Confirmado. <a href="/limpar"> direto. Com loading states (UX-CRIT-01) a consolidacao pode demorar 10-30s — perder tudo por clique errado e altamente provavel. 1h para converter em confirm() ou form POST com modal. |
| UX-HIGH-01 | Encoding quebrado no layout.html — titulo da aba exibe caracteres corrompidos | ALTO | ALTO | 1h | P1 | Confirmado. Arquivo salvo em Windows-1252 ou cp1252 em vez de UTF-8. Afeta todas as paginas. Corrigivel em minutos: re-salvar o arquivo como UTF-8 + verificar Content-Type no Flask. Mantendo em P1 por afetar 100% das interacoes. |
| UX-HIGH-02 | Bug de cor: Novos Inadimplentes e Regua recebem a mesma classe table-cat-a em resultado.html | ALTO | ALTO | 1h | P1 | Confirmado. Lógica Jinja2 no else-if atribui table-cat-a para os dois. Cor table-cat-a (#E3F2FD azul) e usada para ambos. Adicionar table-cat-regua (#E8F5E9 verde claro) resolve. P1 pois afeta a tela central do fluxo diario. |
| UX-HIGH-03 | Sidebar fixa sem comportamento responsivo — tablets: conteudo espremido; mobile: sidebar bloqueia tudo | ALTO | ALTO | 5h | P2 | Estimativa revisada de 6h para 5h. App desktop-only em uso interno: Bootstrap offcanvas para <= 992px e suficiente. Nao requer redesenho completo. Hamburger + offcanvas em layout.html = 5h. Mantido P2 — uso interno desktop. |
| UX-HIGH-04 | Navegacao por hash em configuracoes.html pode nao funcionar na carga inicial | ALTO | MEDIO | 1h | P2 | SEVERIDADE REBAIXADA para MEDIO. Verifiquei o JS: abrirTabPorHash e chamada em DOMContentLoaded. O risco e de timing com o Bootstrap Tab plugin — se o Bootstrap nao inicializou ainda o tab permanece fechado. Bug de baixo impacto operacional (nao bloqueia acesso, apenas abre aba errada). 30min para adicionar await Bootstrap.Tab. |
| UX-HIGH-05 | Tabela de base.html com 13 colunas sem priorizacao — scroll horizontal intenso em 1366px | ALTO | ALTO | 3h | P2 | Confirmado. 13 colunas: #, Nome, CPF, Telefone, Qtd, Total, Ultimo Venc., Dias, Cat., Cobr., Status, Entrada, Acao. Em 1366px (resolucao corporativa padrao) scroll forcado. d-none d-lg-table-cell em CPF e Entrada resolve sem perda funcional. 3h. |
| UX-HIGH-06 | Feedback de Gerar Relatorios depende exclusivamente do flash message — sem confirmacao visual de sucesso | ALTO | ALTO | 2h | P2 | Confirmado. POST sincrono sem loading + redirect + flash. Se o flash for perdido (atualizacao manual) o usuario nao tem feedback. Resolve junto com UX-CRIT-01 (loading) — custo ja incluso ali. Horas aqui: 2h para flash explicito + possivel toast de confirmacao. |
| UX-MED-01 | Badges de categoria inconsistentes entre resultado.html e wizard_whatsapp.html — design system fragmentado | MEDIO | MEDIO | 2h | P2 | Confirmado. badge badge-cat-a (#1565C0 hardcoded) em resultado vs badge bg-primary (Bootstrap) em wizard. Resolver com classes semanticas em layout.html (.badge-cat-novos, .badge-cat-regua, .badge-cat-acima30). Resolve junto com UX-HIGH-02. |
| UX-MED-02 | Input de upload sem preview do arquivo selecionado nem validacao client-side de tipo | MEDIO | MEDIO | 2h | P2 | Confirmado. input[type=file] padrao sem JS de preview. Usuarios carregam o arquivo errado e so descobrem apos POST. JS de 20 linhas mostra nome+tamanho e valida extensao antes do submit. |
| UX-MED-03 | title estatico — em abas multiplas do browser impossivel distinguir qual tela esta aberta | MEDIO | MEDIO | 1h | P2 | Confirmado. layout.html tem <title> estatico. Adicionar {% block title %}{% endblock %} e preencher em cada template = 45min total. |
| UX-MED-04 | Wizard Marcar Todos Enviados sem feedback granular (sem contagem de quantos foram processados) | MEDIO | MEDIO | 1h | P3 | Confirmado. Apos POST /whatsapp/marcar-todos o redirect retorna sem indicar quantos foram marcados. Flash message com contagem = 1h incluindo ajuste no backend para retornar o numero. |
| UX-MED-05 | Modal de edicao de template sem preview ao vivo das variaveis | MEDIO | MEDIO | 3h | P3 | Confirmado. Modal de edicao mostra textarea bruto. A listagem ja faz substituicao de variaveis com JS. Reutilizar a logica no modal = 3h. |
| UX-MED-06 | Filtro de busca em resultado.html nao busca por telefone — inconsistente com wizard_whatsapp.html | MEDIO | BAIXO | 0.5h | P3 | SEVERIDADE REBAIXADA para BAIXO. Telefone e raramente o campo de busca operacional (busca-se por nome). Inconsistencia existe, mas impacto operacional minimo. 30min para adicionar telefone ao data-nome. |
| UX-MED-07 | Tooltip de e-mail via title nativo — nao acessivel em touch nem via leitor de tela | MEDIO | BAIXO | 1h | P3 | SEVERIDADE REBAIXADA para BAIXO. App desktop interno — touch e leitor de tela nao sao use cases prioritarios. Bootstrap data-bs-toggle="tooltip" + aria-label = 1h. Baixo por contexto de uso. |
| UX-LOW-01 | Sem atalhos de teclado para o fluxo diario (Upload, Consolidar, Gerar, Enviar) | BAIXO | BAIXO | 4h | P3 | Confirmado. Operadoras usam mouse no fluxo atual. Atalhos seriam ganho de produtividade, nao correcao de problema. |
| UX-LOW-02 | Sem paginacao ou virtualizacao nas tabelas — degradacao de performance com volume alto | BAIXO | BAIXO | 8h | P3 | Confirmado como Baixo — ver resposta Q-UX-05 para contexto de volume atual. |
| UX-LOW-03 | Cards de mensagem em configuracoes.html sem indicacao de ordem de aplicacao na regua | BAIXO | BAIXO | 1h | P3 | Confirmado. Adicionar numero de sequencia nos cards da aba Mensagens = 1h. |
| UX-LOW-04 | Topbar nao exibe nome da empresa ativa em texto — empresa indicada apenas pela opacidade do logo | BAIXO | MEDIO | 1h | P2 | SEVERIDADE ELEVADA para MEDIO. Ver resposta Q-UX-02. Risco operacional real: empresa errada nao e imediatamente obvio quando so a opacidade do logo diferencia. Nome em texto e essencial. 1h. |
| UX-LOW-05 | Abrir Relatorios sem feedback se a pasta do dia nao existir | BAIXO | BAIXO | 1h | P3 | Confirmado. Link direto para /abrir-relatorios sem validacao. Se a pasta nao existe, comportamento indefinido para o usuario. |

---

## 2. Debito Adicional Identificado

| ID | Debito | Severidade | Horas Est. | Prioridade | Origem |
|----|--------|-----------|------------|------------|--------|
| UX-NEW-01 | Empresa ativa nao validada na carga do wizard — usuario pode iniciar envio de mensagens sem perceber que esta na empresa errada | CRITICO | 2h | P1 | Descoberto na analise de Q-UX-02. O wizard_whatsapp.html nao exibe nenhum indicador da empresa ativa exceto o toggle no topbar (que fica fora do foco visual durante o uso do wizard). Adicionar banner persistente no topo do wizard com nome da empresa ativa. |

---

## 3. Subtotal Revisado

| Categoria | Contagem | Horas |
|-----------|----------|-------|
| Criticos | 4 (3 originais + 1 novo) | 8h |
| Altos | 5 (6 originais - 1 rebaixado) | 12h |
| Medios | 6 (7 originais - 2 rebaixados + 1 elevado) | 10h |
| Baixos | 6 (5 originais + 2 rebaixados) | 15h |
| **Total** | **21 debitos** | **~45h** |

**Variacao em relacao ao DRAFT:** -1h (DRAFT: 46h — estimativa original de 6h para HIGH-03 revisada para 5h).

---

## 4. Respostas as Perguntas do DRAFT (Secao 8)

### Q-UX-01 — Wizard WhatsApp — modo manual vs automatico (Fase H)

**Recomendacao: manter modo manual como fallback permanente.**

O fluxo atual e deliberadamente revisional — a operadora le a mensagem antes de enviar, o que e um controle de qualidade real. O automatico via WAHA/Twilio deve ser um modo adicional, nao um substituto.

**Proposta de interface para dois modos:**
- Adicionar um toggle no cabecalho do wizard: "Modo Manual | Modo Automatico"
- No Modo Manual: comportamento atual intacto
- No Modo Automatico: botao "Disparar Automaticamente" com modal de confirmacao mostrando quantas mensagens serao enviadas, para qual empresa, via qual canal
- Manter a tabela igual em ambos os modos — so o mecanismo de acao muda

**Justificativa:** A Luana (nao tecnica) precisa de um mecanismo de revisao antes do disparo em massa. O risco de enviar mensagem errada para centenas de clientes e alto. O modo manual como fallback tambem resolve falhas de API (WAHA/Twilio offline).

### Q-UX-02 — Indicador visual de empresa ativa — risco de contexto errado

**Tres indicadores complementares recomendados (em ordem de prioridade):**

1. **Nome da empresa em texto no topbar** (UX-LOW-04 elevado para MEDIO): exibir "INEPROTEC" ou "MATRICULAEAD" em texto junto ao toggle — nao apenas logo com opacidade. 1h.

2. **Banner persistente no wizard_whatsapp.html** (UX-NEW-01): faixa colorida no topo da tela de envio mostrando "Enviando para: INEPROTEC" com cor diferenciadora por empresa (ex: azul para Ineprotec, verde para Matricula EAD). O wizard e onde o risco e maximo. 2h.

3. **Confirmacao na troca de empresa**: se houver sessao ativa (pickle carregado), exibir modal ao clicar no toggle: "Voce esta trocando para MATRICULAEAD. Dados consolidados da INEPROTEC nao serao perdidos. Continuar?" Previne troca acidental durante operacao. 2h.

**A mudanca de empresa NAO precisa de digitacao de confirmacao** — isso seria fricção excessiva para uma acao frequente. Confirmacao simples com modal e suficiente.

### Q-UX-03 — configuracoes.html com 29KB e 5 abas — como dividir minimizando impacto

**Recomendacao: NÃO dividir em sub-rotas agora.**

Os sublinks da sidebar (/configuracoes#tab-mensagens) funcionam e a Luana ja conhece a estrutura. Dividir em rotas separadas exigiria:
- Reescrever todos os sublinks da sidebar
- Perder o estado de aba ativa no reload
- Refatorar as 5 funcionalidades em rotas Flask separadas

**Alternativa de menor fricao:**
- Resolver UX-HIGH-04 (timing do hash) = garante que os sublinks funcionem de forma confiavel
- Adicionar lazy loading das 5 abas via JS (so renderiza a aba ativa) = reduz peso de renderizacao
- 29KB de template e aceitavel para uso interno desktop — nao e um problema de performance real agora

**Quando dividir: apenas se/quando o numero de abas ultrapassar 7 ou o tempo de carregamento for perceptivel.**

### Q-UX-04 — Mensagens de erro para operadora nao tecnica — top 5 urgentes

| # | Erro tecnico atual | Mensagem operacional proposta |
|---|--------------------|-------------------------------|
| 1 | pandas KeyError: 'CPF' | "O arquivo de Vencidos nao possui a coluna CPF esperada. Verifique se exportou pelo Synapta e se o arquivo nao esta filtrado." |
| 2 | smtplib.SMTPAuthenticationError | "Credenciais de e-mail incorretas. Use uma Senha de App do Google (nao a senha da conta). Veja o guia em Configuracoes." |
| 3 | FileNotFoundError (pasta vencidos vazia) | "Nenhum arquivo encontrado na pasta Vencidos da [empresa]. Certifique-se de que o arquivo foi copiado para a pasta correta antes de consolidar." |
| 4 | pickle.UnpicklingError (sessao corrompida) | "Dados de consolidacao anteriores estao invalidos. Clique em Limpar Sessao e consolide novamente." |
| 5 | ConnectionRefusedError (SMTP) | "Nao foi possivel conectar ao servidor de e-mail. Verifique se o host e a porta estao corretos em Configuracoes > E-mail." |

**Implementacao:** Adicionar mapeamento de excecoes em app.py — capturar cada tipo de erro e redirecionar com flash message traduzida.

### Q-UX-05 — Volume de dados e virtualizacao de tabelas (UX-LOW-02)

**Resposta baseada nos dados de producao observados (sessao anterior):**

Consolidacao executada com 550 inadimplentes (174 Regua + 376 Acima 30d). Em hardware corporativo tipico (i5, 8GB RAM, Chrome) esse volume renderiza em <500ms — dentro do limiar aceitavel.

**Limiar para virtualizacao: 800-1000 linhas.** Abaixo disso o DOM Bootstrap com table-responsive e performatico o suficiente.

**Classificacao como Baixo esta CORRETA para o volume atual.** Reavaliar se a base crescer para >800 inadimplentes por empresa, o que depende do crescimento das carteiras.

**Recomendacao de acao imediata:** adicionar paginacao simples (Bootstrap 5 `pagination`) mostrando 100 linhas por pagina como medida preventiva de baixo custo (3-4h). Evita o problema antes que ele apareca. Nao requer virtualizacao real (no DOM).

---

## 5. Perguntas para @architect (nao respondidas na Fase 3)

**Q-ARQ-UX-01 — Tempo medio de /consolidar e /gerar-relatorio em producao:**
Com 550 alunos o processamento pandas demora quanto? Acima de 3s o loading state (UX-CRIT-01) e critico. Abaixo de 1s e importante mas nao urgente.

**Q-ARQ-UX-02 — Clipboard API em rede local sem HTTPS:**
O botao Copiar em wizard_whatsapp.html usa navigator.clipboard que requer HTTPS ou localhost. Se a app rodar em http://[ip-local]:5000 em rede interna, o Copiar falha silenciosamente. Confirmar cenario de acesso: localhost apenas ou IP na rede?

**Q-ARQ-UX-03 — Estado da sessao (pickle) e empresa:**
Quando a Luana troca de empresa, o pickle da empresa anterior e mantido em memoria? Se sim, o dado consolidado anterior pode ser acessado via /resultado apos a troca — o que pode causar confusao. Como o estado de empresa e isolado na sessao Flask?

---

*Documento gerado por Uma (@ux-design-expert) — Brownfield Discovery Fase 6 — MAT-INE Inadimplencia 2026*
*Proximo passo: Fase 7 — @qa executa QA Gate (APPROVED / NEEDS WORK)*
