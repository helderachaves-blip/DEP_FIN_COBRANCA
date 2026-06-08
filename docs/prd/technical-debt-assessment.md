# Technical Debt Assessment — FINAL
## MAT-INE Inadimplencia 2026

**Projeto:** MAT-INE Inadimplencia 2026
**Data:** 04/06/2026
**Versao:** Final — aprovado por QA Gate (Fase 7)
**Autores:**
- Aria (@architect) — Fases 1, 4, 8
- Dara (@data-engineer) — Fases 2, 5
- Uma (@ux-design-expert) — Fases 3, 6
- Quinn (@qa) — Fase 7

---

## 1. Resumo Executivo (Corrigido)

| Categoria | Total |
|-----------|-------|
| Total de debitos identificados | **58** |
| Criticos | **10** |
| Altos | **15** |
| Medios | **17** |
| Baixos | **16** |
| Areas afetadas | Sistema (SEC/ARCH/CFG/QUAL), Database (DB), Frontend/UX (UX) |
| Esforco estimado total | **~148h** |

> Nota: O DRAFT inicial declarava 43 debitos. Apos revisao dos especialistas, o total correto e 58: 22 sistema + 14 database + 22 UX (21 originais + UX-NEW-01 descoberto na Fase 6).

**Principais riscos ativos:**
- Credenciais SMTP e secret key expostas — risco de comprometimento imediato em qualquer acesso em rede
- Ausencia total de autenticacao — qualquer rota e publica na rede local
- Acoes destrutivas sem confirmacao (Atualizar Base, Limpar Sessao) — risco diario de perda de dados
- Migracao de banco sem versionamento — estado do schema desconhecido apos qualquer falha
- Empresa errada no wizard de envio — risco operacional critico adicionado na Fase 6

**Bloqueadores absolutos para Fase H (WhatsApp automatico / Twilio):**
1. **SEC-03** — Sem autenticacao: webhook Twilio chegando numa app sem login e vetor de ataque imediato
2. **DB-A01 / ARCH-02** — Sem versionamento de schema: Fase H exige novas colunas; falha sem rollback derruba producao
3. **SEC-01 + DB-C01** — Chave de sessao e senha SMTP expostas: superficie de ataque aumenta com trafego externo

**Decisoes arquiteturais tomadas:**
- Estrategia de migracao: **tabela schema_migrations simples** (nao Alembic) — menor fricao operacional para app mono-usuario em localhost
- Banco canonico: **C:\MATINE\banco\inadimplencia.db** — BASE DE DADOS/inadimplencia.db no repositorio deve ir para .gitignore
- Criptografia SMTP: **Python keyring** — mecanismo mais simples para Windows desktop sem dependencias extras
- Modo de envio Fase H: **dual mode** (Manual como fallback permanente + Automatico via WAHA/Twilio)

---

## 2. Debitos de Sistema

**Validado por:** @architect (Aria) — Brownfield Discovery Fase 1

| ID | Debito | Area | Sev. | Esforco (h) | Prioridade |
|----|--------|------|------|-------------|------------|
| SEC-01 | Secret key de sessao Flask hardcoded em texto plano (app.py ln 38) | Seguranca | CRITICO | 1h | P1 |
| SEC-02 | Senha SMTP armazenada em texto plano no SQLite (tabela config_email) | Seguranca | CRITICO | 3h | P1 |
| SEC-03 | Ausencia total de autenticacao/autorizacao em todas as rotas | Seguranca | CRITICO | 6h | P1 |
| SEC-04 | Pickle para persistencia de estado — risco de deserializacao arbitraria | Seguranca | CRITICO | 4h | P1 |
| ARCH-01 | Dois arquivos inadimplencia.db (producao C:\MATINE + repo BASE DE DADOS) sem documentacao | Arquitetura | ALTO | 2h | P1 |
| ARCH-02 | init_db() com 163 linhas de migracoes acumulativas sem controle de versao | Arquitetura | ALTO | 5h | P1 |
| ARCH-03 | Acoplamento ao Windows via os.startfile() — bloqueia futuros deploys nao-Windows | Arquitetura | ALTO | 2h | P2 |
| ARCH-04 | app.py monolitico com 970+ linhas sem separacao de camadas | Arquitetura | ALTO | 12h | P2 |
| QUAL-01 | Zero testes automatizados para a aplicacao Flask | Qualidade | ALTO | 16h | P2 |
| QUAL-02 | Montagem de e-mail MIME duplicada em dois locais em app.py (ln 718 e 899) | Qualidade | ALTO | 2h | P2 |
| CFG-01 | Dois requirements.txt com versoes conflitantes (raiz vs 06_APP/) | Config | MEDIO | 1h | P2 |
| CFG-02 | Path Python hardcoded para usuario Lorena no launcher .bat | Config | MEDIO | 1h | P2 |
| QUAL-03 | Dead code: gerar_txt() e gerar_xlsx() legadas em processing.py | Qualidade | MEDIO | 1h | P3 |
| QUAL-04 | Ausencia de indices no SQLite — detalhado nos debitos de Database | Qualidade | MEDIO | — | ver DB |
| QUAL-05 | detectar_tratamento() — heuristica de genero fragil com excecoes hardcoded | Qualidade | MEDIO | 2h | P3 |
| QUAL-06 | Validacao de upload somente por extensao (arquivo corrompido aceito silenciosamente) | Qualidade | MEDIO | 2h | P3 |
| QUAL-07 | _carregar_estado() silencia erros de corrupcao de pickle sem log ou alerta | Qualidade | MEDIO | 1h | P2 |
| DOC-01 | README.md desatualizado — descreve app Tkinter legada, nao Flask atual | Documentacao | BAIXO | 2h | P3 |
| DOC-02 | Imports nao utilizados em app.py (json, shutil) | Documentacao | BAIXO | 0.5h | P3 |
| DOC-03 | get_templates() em database.py provavelmente dead code | Documentacao | BAIXO | 0.5h | P3 |
| PERF-01 | Template lookup em loop .iterrows() — aceitavel agora, monitorar na Fase H | Performance | BAIXO | 3h | P3 |
| PERF-02 | Bootstrap e Bootstrap Icons via CDN sem fallback offline | Performance | BAIXO | 2h | P3 |

**Subtotal Sistema:** 22 debitos | Criticos: 4 | Altos: 6 | Medios: 6 | Baixos: 6
**Esforco Sistema:** ~70h

---

## 3. Debitos de Database

**Validado por:** @data-engineer (Dara) — Brownfield Discovery Fase 5

| ID | Debito | Sev. Original | Sev. Final | Esforco (h) | Prioridade | Notas Dara |
|----|--------|--------------|-----------|-------------|------------|-----------|
| DB-C01 | Senha SMTP em texto plano na coluna smtp_senha (database.py ln 513-528) | CRITICO | CRITICO | 3h | P1 | Estimativa ajustada: chave fora do DB + migrar registro existente + atualizar get_config_email + testar SMTP. Mecanismo: Python keyring. |
| DB-C02 | Ausencia total de foreign key constraints + PRAGMA foreign_keys nunca ativado | CRITICO | CRITICO | 3h | P1 | Dados orfaos potenciais. Requer limpeza previa antes de ativar FK. |
| DB-A01 | Schema sem versionamento formal — migracoes inline em init_db() sem schema_migrations nem rollback | ALTO | ALTO | 5h | P1 | Estimativa ajustada de 4h para 5h. 7 fases de migracao misturadas em 163 linhas. Tabela schema_migrations simples recomendada (nao Alembic). |
| DB-A02 | get_envios_hoje() usa LIKE em campo TEXT data_envio — full scan sem indice (ln 495-508) | ALTO | ALTO | 1h | P2 | Indice composto (empresa, data_envio) resolve. |
| DB-A03 | Ausencia de indices em coluna empresa em todas as tabelas operacionais | ALTO | ALTO | 1h | P2 | 5 tabelas, todas filtradas por empresa, nenhum CREATE INDEX. |
| DB-A04 | salvar_base() usa duas conexoes separadas sem transacao atomica (ln 374-449) | ALTO | ALTO | 2h | P2 | Loop de UPSERT sem try/except — falha parcial deixa dados inconsistentes. |
| DB-M01 | Datas armazenadas como TEXT DD/MM/YYYY | MEDIO | MEDIO | 5h | P2 | Estimativa ajustada de 4h para 5h. 5 colunas em 3 tabelas. Depende de DB-A01. |
| DB-M02 | Valores monetarios como REAL (ponto flutuante) — erros de arredondamento | MEDIO | MEDIO | 3h | P3 | INTEGER centavos. Depende de DB-A01. |
| DB-M03 | Sem tabela empresas — discriminador empresa e TEXT livre | MEDIO | MEDIO | 2h | P2 | Criar tabela + FK. Depende de DB-A01. |
| DB-M04 | incrementar_cobrancas() usa executemany sem tratamento de excecao contextualizado | MEDIO | BAIXO | 0.5h | P3 | REBAIXADO: executemany com get_conn() e atomico por default no sqlite3 Python. Gap e apenas de observabilidade. |
| DB-M05 | envios.template_titulo referencia template por TEXT em vez de id INTEGER | MEDIO | MEDIO | 3h | P2 | Rastreabilidade quebrada se template for renomeado. Depende de DB-A01. |
| DB-B01 | get_conn() nao habilita WAL mode | BAIXO | BAIXO | 0.25h | P3 | BLOQUEADOR para Fase H (agendador concorrente) — reclassificar se Fase H avan|car. |
| DB-B02 | Ausencia de estrategia de backup para o SQLite unico | BAIXO | BAIXO | 2h | P2 | DB em C:\MATINE\banco\ — falha de disco = perda total. |
| DB-B03 | Colunas booleanas ativo e smtp_tls sem CHECK constraint | BAIXO | BAIXO | 0.5h | P3 | CHECK via migracao. |

**Subtotal Database:** 14 debitos | Criticos: 2 | Altos: 4 | Medios: 4 | Baixos: 4
**Esforco Database:** ~31h (revisado por Dara — DRAFT era 29h)

---

## 4. Debitos de Frontend/UX

**Validado por:** @ux-design-expert (Uma) — Brownfield Discovery Fase 6

| ID | Debito | Sev. Original | Sev. Final | Esforco (h) | Prioridade | Notas Uma |
|----|--------|--------------|-----------|-------------|------------|-----------|
| UX-NEW-01 | Empresa ativa sem indicador visivel no wizard_whatsapp.html — risco de envio para empresa errada | NOVO | CRITICO | 2h | P1 | Descoberto na Fase 6. O wizard nao exibe empresa ativa alem do toggle no topbar (fora do foco visual durante uso). Banner persistente no topo do wizard com nome da empresa. |
| UX-CRIT-01 | Ausencia total de loading state em acoes sincronas longas (Consolidar, Gerar Relatorios, Atualizar Base, Upload) | CRITICO | CRITICO | 3h | P1 | Estimativa de 4h revisada para 3h — padrao unico para todos os 4 botoes. |
| UX-CRIT-02 | Atualizar Base executa imediatamente sem confirmacao — modifica SQLite permanentemente | CRITICO | CRITICO | 2h | P1 | Dois locais: index.html e resultado.html. Modal Bootstrap recomendado. |
| UX-CRIT-03 | Limpar Sessao executa como link GET sem confirmacao — perda total da consolidacao | CRITICO | CRITICO | 1h | P1 | Converter em form POST com confirm() ou modal. |
| UX-HIGH-01 | Encoding quebrado no layout.html — titulo da aba exibe caracteres corrompidos | ALTO | ALTO | 1h | P1 | Re-salvar como UTF-8 + verificar charset Flask. Afeta 100% das paginas. |
| UX-HIGH-02 | Novos Inadimplentes e Regua recebem a mesma classe table-cat-a em resultado.html | ALTO | ALTO | 1h | P1 | Adicionar table-cat-regua (#E8F5E9 verde claro). Resolve junto com UX-MED-01. |
| UX-HIGH-03 | Sidebar fixa sem comportamento responsivo | ALTO | ALTO | 5h | P2 | Estimativa de 6h revisada para 5h. Bootstrap offcanvas para <= 992px. |
| UX-HIGH-04 | Navegacao por hash em configuracoes.html pode nao funcionar na carga inicial | ALTO | MEDIO | 1h | P2 | REBAIXADO. Bug de timing com Bootstrap Tab plugin. Baixo impacto operacional. |
| UX-HIGH-05 | base.html com 13 colunas sem priorizacao — scroll horizontal intenso em 1366px | ALTO | ALTO | 3h | P2 | Ocultar CPF e Entrada em breakpoints medios. |
| UX-HIGH-06 | Feedback de Gerar Relatorios depende exclusivamente do flash message | ALTO | ALTO | 2h | P2 | Resolve junto com UX-CRIT-01 (loading). Custo separado: flash explicito. |
| UX-LOW-04 | Topbar nao exibe nome da empresa ativa em texto | BAIXO | MEDIO | 1h | P2 | ELEVADO. Risco de contexto errado. Nome em texto junto ao toggle e essencial. |
| UX-MED-01 | Badges de categoria inconsistentes entre resultado.html e wizard_whatsapp.html | MEDIO | MEDIO | 2h | P2 | Classes semanticas em layout.html. Resolve junto com UX-HIGH-02. |
| UX-MED-02 | Input de upload sem preview do arquivo selecionado | MEDIO | MEDIO | 2h | P2 | JS de preview + validacao de extensao antes do submit. |
| UX-MED-03 | Title estatico — impossivel distinguir abas no browser | MEDIO | MEDIO | 1h | P2 | {% block title %} em layout.html + preenchimento em cada template. |
| UX-MED-04 | Wizard Marcar Todos sem feedback granular | MEDIO | MEDIO | 1h | P3 | Flash message com contagem de marcados. |
| UX-MED-05 | Modal de edicao de template sem preview ao vivo | MEDIO | MEDIO | 3h | P3 | Reutilizar logica JS da listagem. |
| UX-MED-06 | Filtro de busca em resultado.html nao busca por telefone | MEDIO | BAIXO | 0.5h | P3 | REBAIXADO. Impacto operacional minimo — busca por nome e o padrao. |
| UX-MED-07 | Tooltip de e-mail via title nativo — nao acessivel | MEDIO | BAIXO | 1h | P3 | REBAIXADO. App desktop interno — touch/leitor de tela nao sao use cases prioritarios. |
| UX-LOW-01 | Sem atalhos de teclado para o fluxo diario | BAIXO | BAIXO | 4h | P3 | Nice-to-have para uso intenso. |
| UX-LOW-02 | Sem paginacao nas tabelas — degradacao com volume alto | BAIXO | BAIXO | 8h | P3 | Volume atual (550 inadimplentes) abaixo do limiar critico (~800-1000 linhas). |
| UX-LOW-03 | Cards de mensagem sem indicacao de ordem na regua | BAIXO | BAIXO | 1h | P3 | Numero de sequencia nos cards da aba Mensagens. |
| UX-LOW-05 | Abrir Relatorios sem feedback se pasta nao existe | BAIXO | BAIXO | 1h | P3 | Validacao no backend + flash message. |

**Subtotal UX:** 22 debitos | Criticos: 4 | Altos: 6 | Medios: 7 | Baixos: 5
**Esforco UX:** ~46h

---

## 5. Totais Consolidados

| Area | Debitos | Criticos | Altos | Medios | Baixos | Horas |
|------|---------|---------|-------|-------|-------|-------|
| Sistema | 22 | 4 | 6 | 6 | 6 | 70h |
| Database | 14 | 2 | 4 | 4 | 4 | 31h |
| UX | 22 | 4 | 6 | 7 | 5 | 46h |
| **Total** | **58** | **10** | **16** | **17** | **15** | **~147h** |

---

## 6. Matriz de Priorizacao Top 12 (Quick Wins + Bloqueadores)

| Rank | ID | Debito | Sev. | Esforco | Justificativa |
|------|-----|--------|------|---------|---------------|
| 1 | SEC-01 | Secret key hardcoded em app.py | CRITICO | 1h | Maximo impacto, minimo esforco — 1 variavel de ambiente resolve |
| 2 | UX-HIGH-01 | Encoding quebrado no titulo | ALTO | 1h | 100% das paginas afetadas, corrigivel em minutos |
| 3 | UX-HIGH-02 | Cores iguais para Novos e Regua | ALTO | 1h | Tela central do fluxo diario indiferenciavel |
| 4 | UX-CRIT-03 | Limpar Sessao sem confirmacao | CRITICO | 1h | Link GET apaga horas de trabalho por clique errado |
| 5 | UX-MED-03 | Title estatico no browser | MEDIO | 1h | {% block title %} resolve em 45min |
| 6 | UX-NEW-01 | Empresa sem indicador no wizard | CRITICO | 2h | Risco operacional critico — cobrar cliente da empresa errada |
| 7 | UX-CRIT-02 | Atualizar Base sem confirmacao | CRITICO | 2h | Acao irreversivel no SQLite sem modal de confirmacao |
| 8 | UX-CRIT-01 | Loading state ausente | CRITICO | 3h | 6 de 8 acoes principais sem feedback — risco de duplo clique |
| 9 | DB-C01 / SEC-02 | Senha SMTP em texto plano | CRITICO | 3h | Credencial corporativa exposta em qualquer backup |
| 10 | DB-C02 | FK constraints ausentes | CRITICO | 3h | limpar_base() cria orfaos silenciosos em envios |
| 11 | DB-A01 / ARCH-02 | Migracoes sem versionamento | ALTO | 5+5h | Bloqueador da Fase H — instala com DB-A01 e ARCH-02 juntos |
| 12 | SEC-03 | Sem autenticacao | CRITICO | 6h | Bloqueador absoluto da Fase H — implementar Flask-Login |

**Esforco Top 12:** ~30h | **Debitos criticos resolvidos:** 8 de 10 | **Bloqueadores Fase H resolvidos:** 3 de 3

---

## 7. Dependencias Entre Debitos

```
SEC-01 (secret key) → resolver ANTES de qualquer acesso em rede
SEC-03 (autenticacao) → resolver ANTES da Fase H
SEC-04 (remover pickle) → resolver JUNTO COM QUAL-07

DB-A01 (schema_migrations) DEVE vir ANTES de qualquer outra migracao:
  DB-C02 (FK constraints) depende de DB-A01
  DB-M01 (datas ISO 8601) depende de DB-A01
  DB-M02 (monetario centavos) depende de DB-A01
  DB-M03 (tabela empresas) depende de DB-A01
  DB-M05 (template_id) depende de DB-A01
  DB-B01 (WAL mode) PODE ser incluido no mesmo patch

ARCH-02 (refatorar init_db) = implementacao pratica de DB-A01
  Incorporar na mesma passagem: DB-A02 (indice envios), DB-A03 (indices empresa)

ARCH-04 (decompor app.py) desbloqueia:
  QUAL-01 (testes — muito mais viavel com camadas separadas)
  QUAL-02 (email duplicado — resolve ao extrair email_service.py)

UX-CRIT-01 (loading states) resolve JUNTO COM UX-HIGH-06 (feedback gerar relatorios)
UX-MED-01 (design system badges) resolve JUNTO COM UX-HIGH-02 (bug cor tabela)
UX-NEW-01 (empresa no wizard) resolve JUNTO COM UX-LOW-04 (empresa na topbar)
```

**Regra critica:** Executar qualquer migracao de schema sem antes implementar DB-A01 repete o padrao que gerou o problema atual.

---

## 8. Decisoes Arquiteturais Registradas

### DA-01: Estrategia de Versionamento de Schema
**Decisao:** Tabela `schema_migrations` simples com scripts numerados.
**Alternativa descartada:** Alembic — overhead injustificado para app mono-usuario em localhost.
**Implementacao:** Criar tabela `schema_migrations(version INTEGER, applied_at TEXT, description TEXT)`. Scripts em `06_APP/migrations/NNN_descricao.py`.

### DA-02: Banco de Dados Canonico
**Decisao:** `C:\MATINE\banco\inadimplencia.db` e o banco de producao.
**Acao:** Adicionar `BASE DE DADOS/inadimplencia.db` ao `.gitignore`. Documentar no README.

### DA-03: Criptografia da Senha SMTP
**Decisao:** Python `keyring` (stdlib adjacente, suporte nativo ao Windows Credential Store).
**Alternativa descartada:** Windows DPAPI via pywin32 — dependencia extra desnecessaria.
**Implementacao:** `keyring.set_password("matine-smtp", empresa, senha)` em vez de coluna `smtp_senha` em texto plano.

### DA-04: Modo de Envio na Fase H
**Decisao:** Dual mode — Manual como fallback permanente, Automatico via WAHA/Twilio como modo adicional.
**Justificativa:** A revisao manual antes do envio e um controle de qualidade deliberado — nao deve ser eliminado.

---

## 9. Proximos Passos

### Sprint Zero (Fase Pre-H) — ~30h — Bloqueadores e Quick Wins
Objetivos: resolver todos os criticos antes de iniciar a Fase H.

**Semana 1 (Quick Wins — 8h):**
- SEC-01: variavel de ambiente para secret key
- UX-HIGH-01: encoding UTF-8 no layout.html
- UX-HIGH-02 + UX-MED-01: corrigir cores + centralizar badges
- UX-CRIT-03: confirmacao no Limpar Sessao
- UX-MED-03: {% block title %} dinamico
- UX-NEW-01 + UX-LOW-04: indicador de empresa no wizard + topbar

**Semana 2 (Seguranca UX — 8h):**
- UX-CRIT-01: loading states em todos os form POST
- UX-CRIT-02: modal confirmacao Atualizar Base
- DB-C01 / SEC-02: keyring para senha SMTP

**Semana 3 (Database Foundation — 12h):**
- DB-A01 / ARCH-02: schema_migrations + refatorar init_db()
- DB-C02: FK constraints com limpeza previa
- DB-A02 + DB-A03 + DB-B01: indices + WAL mode (no mesmo patch)

**Semana 4 (Autenticacao + Buffer — 6h):**
- SEC-03: Flask-Login com usuario unico hardcoded (MVP de autenticacao)

### Sprint 1 (Estabilizacao — P2/P3)
Apos Sprint Zero: ARCH-04 (decompor app.py) → QUAL-01 (testes) → UX-HIGH-03 (responsividade) → restante dos medios.

---

*Documento final gerado por Aria (@architect) — Brownfield Discovery Fase 8 — MAT-INE Inadimplencia 2026*
*Referencia: QA Gate aprovado em docs/reviews/qa-review.md*
*Proximo passo: Fase 9 — @analyst gera relatorio executivo*
