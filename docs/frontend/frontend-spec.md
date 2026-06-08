# Frontend Specification — MAT-INE Inadimplência 2026

**Gerado por:** @ux-design-expert (Uma) — Brownfield Discovery Fase 3  
**Data:** 2026-06-04  
**Escopo:** Templates Flask + Bootstrap 5 — `/06_APP/templates/`

---

## 1. Visão Geral do Frontend

O frontend do MAT-INE Inadimplência 2026 é uma aplicação web interna (single-user / operacional) construída sobre Flask com Jinja2 como motor de templates. Toda a camada de apresentação é baseada em Bootstrap 5.3.3 + Bootstrap Icons 1.11.3 via CDN. Não há build system, bundler ou framework JS — todo JavaScript é vanilla inline nos próprios templates.

**Perfil de uso:** operadores do setor financeiro das empresas Ineprotec e Matrícula EAD, acesso via desktop interno (Windows), fluxo diário repetitivo de carga + consolidação + envio de cobranças.

**Stack visual:**

| Camada | Tecnologia | Versão |
|---|---|---|
| CSS Framework | Bootstrap | 5.3.3 (CDN) |
| Ícones | Bootstrap Icons | 1.11.3 (CDN) |
| Fonte | Segoe UI (sistema) | — |
| JavaScript | Vanilla ES6 inline | — |
| Templates | Jinja2 (Flask) | — |
| Dados | Jinja2 server-side render | — |

**Páginas existentes:**

| Rota | Template | Função |
|---|---|---|
| `/` | `index.html` | Upload de arquivos + ações principais |
| `/resultado` | `resultado.html` | Tabela consolidada + cards de resumo |
| `/wizard-whatsapp` | `wizard_whatsapp.html` | Envio de mensagens WhatsApp/e-mail |
| `/base` | `base.html` | Gestão da base SQLite de inadimplentes |
| `/configuracoes` | `configuracoes.html` | Templates de mensagem, régua, e-mail, zona de risco |

**Arquitetura de layout:** `layout.html` é o master template (extends). Toda página hereda sidebar fixa + topbar + área de conteúdo. Flash messages são exibidas globalmente no `layout.html`.

---

## 2. Componentes e Design System

### 2.1 Layout Estrutural

**Sidebar** (`layout.html`)
- Largura fixa: `230px`, cor `#1a1a2e` (dark navy)
- `position: fixed` — ocupa toda altura da viewport
- Navegação com `nav-link` para 5 seções: Início, Resultado, Envio de Mensagens, Base, Configurações
- Configurações tem submenu colapsável (Bootstrap Collapse) com 5 sublinks: Mensagens, Régua, Clientes, E-mail, Zona de Risco
- Link ativo: `border-left: 3px solid #a0c4ff` + background translúcido + cor `#a0c4ff`
- Estado ativo determinado via `request.endpoint` (Jinja2)

**Topbar** (`layout.html`)
- Cor `#1a1a2e` (mesma da sidebar), `position: sticky; top: 0`
- Contém: logo Ineprotec (esquerda) + toggle de empresa (centro) + logo Matrícula EAD (direita)
- Toggle de empresa: pill com dois botões; logo da empresa inativa fica com `opacity: 0.35`
- Troca de empresa via link `url_for('trocar_empresa')`

**Content Area**
- `margin-left: 230px` para compensar sidebar fixa
- Padding: `1.5rem 1.75rem`
- Background: `#f5f6fa`

### 2.2 Cards

Padrão único em todas as páginas:
- `border: none; box-shadow: 0 2px 8px rgba(0,0,0,.08); border-radius: 12px`
- `card-header`: fundo `#1a1a2e`, texto branco, `font-weight: 600`
- Variações: `border-start border-4 border-{color}` para cards de totalizador (resultado.html)
- Cards de mensagem (configuracoes.html): `border-start border-4 border-{success|primary|danger|warning}` por categoria

### 2.3 Stat Cards

Componente de KPI visual usado em `index.html` e `resultado.html`:
- Classe `.stat-card` + variantes `.azul`, `.verde`, `.vermelho`, `.laranja`
- Gradientes: azul `#1565C0→#42A5F5`, verde `#2e7d32→#66bb6a`, vermelho `#b71c1c→#ef5350`, laranja `#e65100→#ffa726`
- Número: `.stat-num` (`font-size: 2rem; font-weight: 700`)
- Rótulo: `.stat-label` (`font-size: .85rem; opacity: .9`)
- Stat cards em `resultado.html` são clicáveis (filtro por categoria) — indicado por `cursor:pointer` + `title="Clique para filtrar"`

### 2.4 Badges / Status

| Classe | Cor | Uso |
|---|---|---|
| `.badge-cat-a` | `#1565C0` (azul) | Régua (vencidos 2-29d) |
| `.badge-cat-b` | `#B71C1C` (vermelho escuro) | Acima 30 dias |
| `.badge-inadimplente` | `#d32f2f` | Status inadimplente (base.html) |
| `.badge-quitado` | `#388e3c` (verde) | Status quitado |
| `.badge-renegociado` | `#f57c00` (laranja) | Status renegociado |
| `bg-success` | Bootstrap | Novos inadimplentes, enviado |
| `bg-danger` | Bootstrap | Acima 30 dias, dias badge |
| `bg-warning text-dark` | Bootstrap | Dias badge 1-30 |

**Inconsistência identificada:** a mesma categoria "Régua" usa `badge badge-cat-a` em `resultado.html` mas `badge bg-primary` em `wizard_whatsapp.html`. Ambas resultam em azul, mas a implementação é duplicada e inconsistente.

### 2.5 Tabelas

- Bootstrap `table table-hover` com `thead class="table-dark"`
- `table-responsive` wrapping em todas as páginas
- Linhas coloridas por categoria: `.table-cat-a` (`#E3F2FD` azul claro) e `.table-cat-b` (`#FFEBEE` vermelho claro)
- Linhas enviadas em `wizard_whatsapp.html`: `table-success`

**Bug de cor em resultado.html:** A categoria "Régua" recebe `table-cat-a` (mesmo que "Novos Inadimplentes") em vez de uma cor distinta — a lógica Jinja2 tem o segundo else-if também atribuindo `table-cat-a`. "Novos" e "Régua" ficam com a mesma cor de linha — indiferenciáveis visualmente.

### 2.6 Formulários

- `form-control form-control-sm` para inputs compactos
- Upload de arquivos: `input[type=file]` Bootstrap nativo sem customização
- Filtros inline em cards com row/col Bootstrap
- Modal Bootstrap para ações destrutivas (excluir template, limpar base, alterar status)

### 2.7 Feedback / Toast

`wizard_whatsapp.html` possui um toast Bootstrap posicionado `bottom-0 end-0` para feedback de ações assíncronas (copiar, marcar enviado, enviar e-mail). Cor dinâmica (`bg-primary`, `bg-success`, `bg-danger`). Delay de 2500ms.

### 2.8 Barra de Progresso

`wizard_whatsapp.html` tem progress bar Bootstrap (`bg-success`) com transição CSS `.4s` exibindo `X/Y enviados` e percentual. Atualização via JavaScript após cada ação de marcar enviado.

---

## 3. Fluxos de Usuário

### Fluxo Principal (operação diária)

```
[Início /]
  ├── Upload arquivo "Faturas Vencidas" (.csv/.xlsx)
  ├── Upload arquivo "Faturas À Vencer" (.csv/.xlsx)
  ├── [Consolidar Agora] → POST /consolidar (redirect para mesma página)
  │     ↓ (sem loading state — formulário HTML síncrono)
  ├── Visualizar stat cards de resultado (Novos / Régua / Acima 30d / Valor)
  ├── [Ver Tabela de Resultado] → GET /resultado
  ├── [Gerar Relatórios WhatsApp] → POST /gerar-relatorio
  ├── [Comparar e Atualizar Base] → POST /atualizar-base
  └── [Limpar Sessão] → GET /limpar
```

### Fluxo de Envio de Mensagens

```
[Resultado /resultado]
  └── [Envio de Mensagens] → GET /wizard-whatsapp
        ├── Filtrar por categoria / nome / "ocultar enviados"
        ├── Clicar na linha → expandir mensagem (Bootstrap Collapse)
        ├── [Copiar] → clipboard API → toast feedback
        ├── [Envelope] → POST /email/enviar-aluno → toast feedback
        ├── [Check] → POST /whatsapp/marcar-enviado → atualiza linha (verde) + progresso
        ├── [Enviar E-mail para Todos] → POST /email/enviar-todos (confirm dialog)
        └── [Marcar Todos Enviados] → POST /whatsapp/marcar-todos (confirm dialog)
```

### Fluxo de Configuração (setup / manutenção)

```
[Configurações /configuracoes]
  ├── Tab Mensagens → CRUD de templates WhatsApp (modais)
  ├── Tab Régua → visualização read-only da régua gerada automaticamente
  ├── Tab Clientes → upload de arquivo de cadastro (Synapta)
  ├── Tab E-mail → config SMTP + assuntos por template
  └── Tab Zona de Risco → Limpar Base (modal com digitação de confirmação "LIMPAR")
```

### Fluxo de Gestão da Base

```
[Base /base]
  ├── Filtrar por status / categoria / nome
  └── [Lápis] → modal Bootstrap → alterar status (INADIMPLENTE / QUITADO / RENEGOCIADO)
```

### Navegação por Hash (Configurações)

`configuracoes.html` suporta abertura de aba via hash da URL (`/configuracoes#tab-mensagens`). Os sublinks da sidebar usam essa convenção. Implementado via JavaScript no bloco scripts.

---

## 4. Análise de Responsividade

### Situação Geral

A aplicação é desktop-first, projetada para uso interno em Windows. Não há preocupação declarada com mobile. No entanto, os breakpoints Bootstrap estão parcialmente configurados.

### Por Componente

**Sidebar (`layout.html`)**
- `position: fixed; width: 230px` — sem comportamento responsivo. Em telas menores que 992px a sidebar permanece visível e consume 230px do viewport. Não há botão de hamburger ou mecanismo de colapso.
- Em tablets (768px-991px) o conteúdo fica espremido.
- Em mobile (menor que 768px) a sidebar sobrepõe 100% do conteúdo.

**Topbar (`layout.html`)**
- Toggle de empresa usa `white-space: nowrap` — não colapsa em telas pequenas.
- Os dois logos + toggle podem sobrepor em viewports menores que 600px.

**Index (`index.html`)**
- Grid `col-lg-6` para os dois cards principais — em telas menores que 992px ficam em coluna única (adequado).
- Stat cards usam `col-md-4` — em mobile empilham (adequado).
- Botões de upload: `d-flex gap-2` — em viewport menor que 400px o botão "Importar" pode ficar cortado.

**Resultado (`resultado.html`)**
- Botões de ação: `col-12 col-sm-6 col-md-3` — respondem bem.
- Stat cards: layout condicional baseado em `avencer_linhas` — complexo mas funcional.
- Tabela principal: `table-responsive` — scroll horizontal em mobile.
- Colunas ocultas em mobile: nenhuma — todas as 8 colunas aparecem, forçando scroll.

**Wizard WhatsApp (`wizard_whatsapp.html`)**
- Filtros: `row g-2 align-items-center` com `col-auto` e `col` — colapsa aceitavelmente.
- Tabela: 7 colunas sem breakpoint de ocultação.
- Botões de ação no cabeçalho: `d-flex gap-2 flex-wrap` — wrapping adequado.

**Configurações (`configuracoes.html`)**
- `col-lg-9` limita largura máxima — bom para leitura.
- Nav tabs horizontais: sem scroll em mobile (Bootstrap padrão — trunca em viewports estreitos).
- Formulário SMTP: `col-md-6 / col-md-2 / col-md-4` — colapsa em mobile.

### Sumário de Responsividade

| Página | Desktop | Tablet (768-991px) | Mobile (menor que 768px) |
|---|---|---|---|
| layout (sidebar) | OK | PARCIAL | QUEBRADO |
| index.html | OK | OK | OK |
| resultado.html | OK | OK | SCROLL INTENSO |
| wizard_whatsapp.html | OK | OK | SCROLL INTENSO |
| base.html | OK | OK | SCROLL INTENSO (13 colunas) |
| configuracoes.html | OK | OK | PARCIAL |

---

## 5. Estados da Interface (loading, erro, vazio, sucesso)

### 5.1 Loading States

| Ação | Estado de Loading |
|---|---|
| Upload de arquivo (`/upload`) | AUSENTE — form submit síncrono, página congela |
| Consolidar (`/consolidar`) | AUSENTE — form submit síncrono, pode demorar vários segundos |
| Gerar Relatórios (`/gerar-relatorio`) | AUSENTE |
| Comparar e Atualizar Base (`/atualizar-base`) | AUSENTE |
| Enviar e-mail individual | PRESENTE — `spinner-border spinner-border-sm` no botão durante fetch |
| Copiar mensagem | PRESENTE — ícone muda para `bi-check2` por 1,6s |
| Marcar como enviado | AUSENTE — fetch assíncrono sem indicação visual durante a requisição |
| Testar conexão SMTP (`/email/testar`) | AUSENTE — form submit síncrono |

**Diagnóstico:** 6 das 8 ações principais não têm loading state. As ações síncronas (form POST) podem demorar de 1s a 15s+ dependendo do volume de dados, sem nenhum feedback visual ao usuário.

### 5.2 Estados de Erro

| Contexto | Tratamento |
|---|---|
| Flash messages (Flask) | PRESENTE via `layout.html` — `alert alert-{cat} alert-dismissible` |
| Erro no fetch (marcar enviado) | PRESENTE — toast `bg-danger` "Erro ao marcar" |
| Erro no fetch (enviar e-mail) | PRESENTE — toast `bg-danger` com `data.erro` |
| Erro na clipboard API | PRESENTE — toast "Erro ao copiar" |
| Arquivo não importado | PRESENTE — badge `bg-warning` "Nenhum arquivo importado" |
| Base vazia | PRESENTE — `alert alert-info` em `base.html` |
| Sem consolidação no resultado | PRESENTE — `alert alert-warning` com link para início |
| Sem templates configurados (wizard) | PRESENTE — `alert alert-warning` com link para configurações |
| Erros de validação de formulário | AUSENTE — não há validação client-side; erros chegam apenas via flash |
| Timeout/falha no consolidar | AUSENTE — sem tratamento de erro específico |

### 5.3 Estados Vazios

| Tela | Estado Vazio |
|---|---|
| index.html sem consolidação | Card cinza com ícone e texto explicativo — BOM |
| base.html sem dados | `alert alert-info` com instrução — BOM |
| resultado.html sem consolidação | `alert alert-warning` — BOM |
| wizard sem templates | `alert alert-warning` — BOM |
| configuracoes tab-regua sem templates | Linha na tabela com texto e link — BOM |

### 5.4 Estados de Sucesso

| Ação | Feedback de Sucesso |
|---|---|
| Upload de arquivo | Badge `bg-success` "Arquivo presente" com nome — BOM |
| Consolidação completa | Stat cards + botões habilitados (mudança de estado da tela) — BOM |
| Marcar como enviado | Linha fica `table-success` + badge `bi-check2-all` + toast + progresso — EXCELENTE |
| E-mail enviado individualmente | Botão troca para `btn-info` + `bi-envelope-check` + toast — BOM |
| Salvar configurações SMTP | Flash message (vinda do Flask) — ADEQUADO |
| Alterar status base | Redirect + flash message — ADEQUADO |
| Limpar base | Modal com digitação de confirmação + redirect — BOM |

---

## 6. Acessibilidade

### 6.1 Semântica HTML

| Elemento | Situação |
|---|---|
| `<html lang="pt-BR">` | PRESENTE — correto |
| `<title>` | PRESENTE — com encoding quebrado no arquivo fonte (ver UX-HIGH-01) |
| `<aside>` para sidebar | PRESENTE — correto |
| `<nav>` dentro de aside | PRESENTE — correto |
| Roles em tabs (tablist/tab/tabpanel) | PRESENTES em configuracoes.html — correto |
| `aria-expanded` no submenu colapsável | PRESENTE — correto |
| `aria-controls` no submenu | PRESENTE — correto |
| `role="progressbar"` na progress bar | PRESENTE em wizard_whatsapp.html — correto |
| `role="alert"` nos toasts | PRESENTE — correto |
| `tabindex="-1"` nos modais | PRESENTE — correto |

### 6.2 Formulários e Labels

| Situação | Avaliação |
|---|---|
| Labels para todos os inputs de configuracoes.html | PRESENTE |
| Labels para inputs de upload (index.html) | AUSENTE — `form-label` presente mas sem `for` vinculado ao `input` |
| Labels para filtros | PRESENTE na maioria, mas sem atributo `for` em alguns |
| Campos obrigatórios marcados com `*` e `text-danger` | PRESENTE em configuracoes.html |
| Atributo `required` nos campos obrigatórios | PRESENTE nos modais de template |

### 6.3 Contraste e Cores

| Combinação | Ratio Estimado | Status |
|---|---|---|
| Texto branco sobre `#1a1a2e` (sidebar/topbar/headers) | ~15:1 | PASSOU |
| `rgba(255,255,255,.68)` sobre `#1a1a2e` (nav-link) | ~8:1 | PASSOU |
| `.stat-label` `opacity:.9` branco sobre gradiente verde | ~4:1 | LIMITE |
| Badge `bg-warning text-dark` | ~4.5:1 | PASSA (WCAG AA) |
| `text-muted` (`#6c757d`) sobre `#f5f6fa` (fundo) | ~3.9:1 | REPROVADO (WCAG AA = 4.5:1) |
| Código fonte em `font-monospace text-secondary` sobre `#f8f9fa` | ~3.2:1 | REPROVADO |

### 6.4 Interatividade

| Situação | Avaliação |
|---|---|
| Linhas de tabela clicáveis (wizard) com `style="cursor:pointer"` | SEM `role="button"` ou `tabindex` — não acessível via teclado |
| Botões com apenas ícone (lápis, trash, clipboard) | `title` presente, mas sem `aria-label` explícito |
| Stat cards clicáveis com `cursor:pointer` | SEM `role="button"`, `tabindex` ou indicação textual de interatividade |
| Toast com `role="alert"` | Correto para leitores de tela |
| Modal com foco gerenciado pelo Bootstrap | Bootstrap 5 gerencia foco automaticamente — adequado |

### 6.5 Movimento e Animação

- Transições CSS presentes: `transition: background .15s` (nav-links), `transition: width .4s` (progress bar), `opacity: 0.35 → 1` (logos topbar)
- Não há `prefers-reduced-motion` respeitado — baixo impacto dado o contexto de uso interno

---

## 7. Débitos UX/UI Identificados

### 7.1 Críticos (bloqueiam uso ou causam perda de dados)

**UX-CRIT-01 — Ausência total de loading state em ações síncronas longas**
- **Páginas:** `index.html` (botões Consolidar, Gerar Relatórios, Atualizar Base, Upload)
- **Problema:** Todas as ações de processamento são form POST síncrono. O botão não desabilita, a página não dá feedback. O usuário não sabe se o sistema está processando ou travado. Pode clicar múltiplas vezes, gerando processamentos duplicados.
- **Impacto:** Alto risco de duplo clique em "Consolidar" ou "Atualizar Base", corrompendo dados.
- **Solução:** Desabilitar botão no `submit` via JS + exibir spinner inline no botão.

**UX-CRIT-02 — Ação destrutiva "Comparar e Atualizar Base" sem confirmação**
- **Páginas:** `index.html` e `resultado.html`
- **Problema:** O botão "Comparar e Atualizar Base" (`btn-warning`) executa imediatamente ao clique, sem modal de confirmação nem digitação de segurança. Essa ação modifica a base SQLite permanentemente.
- **Contraste:** "Limpar Base" em Configurações tem modal + digitação de "LIMPAR". Inconsistência grave.
- **Solução:** Adicionar `onclick="return confirm(...)"` como mínimo, ou modal similar ao de Limpar Base.

**UX-CRIT-03 — "Limpar Sessão" sem confirmação e sem destaque de perigo**
- **Página:** `index.html`
- **Problema:** `<a href="/limpar" class="btn btn-outline-secondary btn-sm">` — link direto sem confirmação. Ao clicar acidentalmente, toda a sessão de consolidação é perdida.
- **Solução:** `onclick="return confirm('Tem certeza? Isso apagará a consolidação atual.')"` ou transformar em form POST com modal.

### 7.2 Altos (prejudicam significativamente a experiência)

**UX-HIGH-01 — Encoding quebrado no título do layout.html**
- **Página:** `layout.html` (afeta todas as páginas)
- **Problema:** O arquivo `layout.html` está salvo com encoding diferente do UTF-8 ou o servidor não está enviando o charset correto. O título da aba do browser exibe "CobranÃ§as â€" Ineprotec / MatrÃ­cula EAD" em vez do texto correto.
- **Solução:** Verificar encoding do arquivo fonte + assegurar `Content-Type: text/html; charset=utf-8` nas respostas Flask.

**UX-HIGH-02 — Linhas de tabela "Novos Inadimplentes" e "Régua" indistinguíveis**
- **Página:** `resultado.html`
- **Problema:** Bug na lógica de cor da linha — ambas as categorias recebem `table-cat-a` (`#E3F2FD`). O usuário não consegue distinguir visualmente as duas categorias na tabela, dependendo exclusivamente do badge na coluna "Categoria".
- **Solução:** Separar classes: `table-cat-a` para Novos, nova classe `table-cat-regua` (ex: `#E8F5E9` verde claro) para Régua.

**UX-HIGH-03 — Sidebar sem comportamento responsivo / sem toggle mobile**
- **Página:** `layout.html` (afeta todas as páginas)
- **Problema:** A sidebar fixa de 230px não colapsa em telas menores. Em tablets, o conteúdo fica espremido. Em mobile, a sidebar bloqueia todo o conteúdo.
- **Impacto:** Médio — uso interno em desktop, mas qualquer consulta emergencial em tablet fica inacessível.
- **Solução:** Adicionar botão hamburger + `offcanvas` Bootstrap para sidebar em telas menores que 992px.

**UX-HIGH-04 — Navegação por hash pode não funcionar na carga inicial**
- **Página:** `configuracoes.html`
- **Problema:** Os sublinks da sidebar usam `href="/configuracoes#tab-mensagens"` para abrir a aba correta. Se a função `abrirTabPorHash` não for chamada em `DOMContentLoaded`, os sublinks abrem a página sempre na aba "Mensagens" (primeira aba), ignorando o hash.
- **Solução:** Assegurar que a função seja chamada em `DOMContentLoaded` com `window.location.hash`.

**UX-HIGH-05 — Tabela da Base de Dados com 13 colunas sem priorização**
- **Página:** `base.html`
- **Problema:** A tabela tem 13 colunas: #, Nome, CPF, Telefone, Qtd, Total, Último Vencimento, Dias, Cat., Cobr., Status, Entrada, Ação. Em resolução 1366px (comum em notebooks corporativos), haverá scroll horizontal e leitura difícil.
- **Solução:** Ocultar colunas de menor prioridade em breakpoints menores (`d-none d-lg-table-cell`), especialmente CPF e Entrada.

**UX-HIGH-06 — Feedback de "Gerar Relatórios" sem confirmação de sucesso na tela**
- **Páginas:** `index.html` / `resultado.html`
- **Problema:** O botão "Gerar Relatórios WhatsApp" faz POST síncrono. O feedback depende inteiramente do flash message do Flask — se o redirect falhar ou o flash for perdido, o usuário fica sem saber se os relatórios foram gerados.
- **Solução:** Flash message explícita + redirecionar para `/resultado` com feedback claro após geração.

### 7.3 Médios (melhorias importantes para a experiência)

**UX-MED-01 — Badges de categoria inconsistentes entre resultado.html e wizard_whatsapp.html**
- **Problema:** "Régua" usa `badge badge-cat-a` (cor hardcoded `#1565C0`) em `resultado.html` mas `badge bg-primary` (cor Bootstrap) em `wizard_whatsapp.html`. O design system está fragmentado.
- **Solução:** Criar classes utilitárias únicas (ex: `.badge-categoria-regua`, `.badge-categoria-novos`, `.badge-categoria-acima30`) definidas em `layout.html` e usadas consistentemente.

**UX-MED-02 — Input de upload sem preview do arquivo selecionado antes do envio**
- **Página:** `index.html`
- **Problema:** O campo `input[type=file]` é o padrão Bootstrap sem customização. Não há preview do nome/tamanho antes de submeter, não há validação de tipo de arquivo no client-side.
- **Solução:** JS para mostrar nome do arquivo selecionado + validação de extensão antes do submit.

**UX-MED-03 — Título da página não muda por rota**
- **Problema:** O `<title>` em `layout.html` é estático. Nenhuma página filha sobrescreve o título. Em abas múltiplas do browser, é impossível distinguir qual aba é qual tela.
- **Solução:** Adicionar `{% block title %}{% endblock %}` em `layout.html` e definir título específico em cada template filho.

**UX-MED-04 — Wizard WhatsApp: "Marcar Todos" sem feedback granular**
- **Página:** `wizard_whatsapp.html`
- **Problema:** O botão "Marcar Todos Enviados" usa `confirm()` e faz POST síncrono. Após o redirect, não há indicação de quantos foram marcados ou se houve erro.
- **Solução:** Flash message com contagem: "X clientes marcados como enviados."

**UX-MED-05 — Templates de mensagem sem preview ao vivo no modal de edição**
- **Página:** `configuracoes.html` (modal de edição)
- **Problema:** O modal de edição mostra o textarea com variáveis brutas. A listagem principal tem preview substituído com dados reais, mas o modal de edição não.
- **Solução:** Adicionar preview ao vivo no modal de edição, igual ao que a listagem já faz.

**UX-MED-06 — Filtro de busca em resultado.html não busca por telefone**
- **Página:** `resultado.html`
- **Problema:** O placeholder diz "Buscar por nome..." e a lógica JS usa `tr.dataset.nome.includes(busca)`. Em `wizard_whatsapp.html` o dataset concatena nome + telefone. Inconsistência entre telas.
- **Solução:** Adicionar telefone ao `data-nome` em `resultado.html` e atualizar o placeholder.

**UX-MED-07 — Tooltip de e-mail via `title` não é acessível**
- **Páginas:** `wizard_whatsapp.html` e `base.html`
- **Problema:** O ícone de envelope usa `title="{{ l.email }}"` para mostrar o e-mail. `title` nativo não é acessível em dispositivos touch nem por leitores de tela de forma confiável.
- **Solução:** Substituir por Bootstrap `data-bs-toggle="tooltip"` com `aria-label`.

### 7.4 Baixos (nice-to-have)

**UX-LOW-01 — Sem atalhos de teclado para ações frequentes**
- O fluxo diário (Upload → Consolidar → Gerar → Enviar) não tem atalhos. Para uso intenso, teclas de atalho aumentariam a eficiência operacional.

**UX-LOW-02 — Sem paginação ou virtualização nas tabelas**
- Com volume alto de inadimplentes (centenas/milhares de linhas), as tabelas de `resultado.html`, `wizard_whatsapp.html` e `base.html` renderizam todas as linhas no DOM. Sem virtualização, o desempenho degradará.

**UX-LOW-03 — Cards de mensagem em configuracoes.html sem indicação de ordem de aplicação**
- A aba "Régua" mostra a sequência ordenada, mas a aba "Mensagens" lista sem ordem aparente. Um número de sequência tornaria a gestão mais intuitiva.

**UX-LOW-04 — Topbar não exibe o nome da empresa ativa em texto**
- A empresa ativa é indicada apenas pela opacidade do logo (1.0 vs 0.35). Seria mais claro exibir o nome da empresa ativa em texto junto ao toggle.

**UX-LOW-05 — Botão "Abrir Relatórios" sem feedback se a pasta não existe**
- `<a href="/abrir-relatorios">` — se a pasta do dia não existir, o comportamento não é comunicado ao usuário.

---

## 8. Recomendações de Design

### 8.1 Prioridade Imediata (sprint atual)

1. **Desabilitar botões de ação durante processamento** — implementar em todos os form POST síncronos (`consolidar`, `gerar-relatorio`, `atualizar-base`, `upload`). Padrão: `btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Processando...'` no evento `submit`.

2. **Adicionar confirmação em "Comparar e Atualizar Base"** — mínimo `onclick="return confirm(...)"` ou modal Bootstrap (preferível, para consistência com o modal de "Limpar Base").

3. **Corrigir o bug de cor de linha em resultado.html** — separar `table-cat-a` de uma nova classe para "Régua".

4. **Adicionar bloco `title` no layout.html** — muda sem impacto em nada existente; cada página adiciona seu título específico.

### 8.2 Próximo Sprint

5. **Centralizar o design system de badges** — criar classes semânticas em `layout.html` para eliminar as inconsistências de badge entre páginas.

6. **Ocultar colunas não-essenciais em breakpoints médios** — principalmente em `base.html` (CPF, Entrada) e `resultado.html` em mobile.

7. **Validação client-side nos formulários de configuração** — campos SMTP obrigatórios com feedback imediato.

8. **Adicionar `aria-label` nos botões icon-only** — todos os botões que têm apenas ícone precisam de `aria-label` descritivo.

### 8.3 Backlog de Melhoria

9. **Sidebar responsiva com offcanvas** — para uso em tablets e consultas emergenciais em mobile.

10. **Preview ao vivo no modal de edição de template** — reaproveitar a lógica de substituição de variáveis já presente na listagem.

11. **Busca por telefone em resultado.html** — alinhar com o comportamento de wizard_whatsapp.html.

12. **Toast ou flash para "Marcar Todos Enviados"** — contador de quantos foram processados.

---

## 9. Perguntas para @architect

1. **Volume de dados esperado:** Qual o número máximo estimado de inadimplentes por empresa por ciclo? Isso define se virtualização de tabelas é necessária (acima de ~500 linhas o DOM fica pesado sem paginação).

2. **Multi-usuário:** A aplicação é mono-usuário (um operador por vez) ou pode haver acesso simultâneo? Isso impacta a gestão de estado de sessão Flask e os indicadores de "enviado hoje".

3. **Tempo médio de processamento:** Quanto tempo demora o endpoint `/consolidar` e `/gerar-relatorio` em produção? Isso define a prioridade do loading state — se for menos de 1s não é crítico, se for acima de 3s é urgente.

4. **Encoding do layout.html:** O template tem encoding quebrado no título. O Flask está servindo com `utf-8`? Há algum middleware ou configuração de charset? Ou o arquivo foi salvo com Windows-1252?

5. **Persistência de sessão:** Os dados de consolidação ficam em memória (Flask session) ou em banco? Se em memória, um reload do servidor perde tudo — o usuário deveria ser avisado disso.

6. **HTTPS / proxy reverso:** A API `navigator.clipboard` (usada para copiar mensagens) requer HTTPS ou `localhost`. Se a aplicação rodar em HTTP em rede local, o botão "Copiar" falhará silenciosamente ou exibirá toast de erro. Isso está sendo tratado?

7. **Autenticação:** Não há nenhum mecanismo de login visível nos templates. A aplicação é exposta apenas em rede interna? Há plano de autenticação futura?

8. **Empresa ativa e estado global:** O toggle de empresa sugere que existem dados separados por empresa. A sidebar e o título da página deveriam refletir a empresa ativa? Atualmente o título é estático e não indica para qual empresa os dados estão sendo exibidos.

---

*Frontend Specification gerada pela análise de 6 templates: layout.html, index.html, resultado.html, wizard_whatsapp.html, base.html, configuracoes.html*  
*@ux-design-expert (Uma) — Brownfield Discovery Fase 3 — MAT-INE Inadimplência 2026*
