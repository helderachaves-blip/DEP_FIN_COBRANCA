# Technical Debt Assessment — DRAFT
## Para Revisão dos Especialistas

**Projeto:** MAT-INE Inadimplência 2026
**Data:** 04/06/2026
**Status:** DRAFT — Aguardando validação de @data-engineer e @ux-design-expert
**Autor:** Aria (@architect) — Brownfield Discovery Fase 4

---

## 1. Resumo Executivo

| Categoria | Total |
|-----------|-------|
| Total de débitos identificados | 43 |
| Críticos | 8 |
| Altos | 13 |
| Médios | 14 |
| Baixos | 8 |
| Áreas afetadas | Sistema (SEC/ARCH/CFG/QUAL), Database (DB), Frontend/UX (UX) |

**Principais riscos ativos:**
- Credenciais SMTP e secret key expostas em texto plano — risco de comprometimento imediato
- Ausência total de autenticação — qualquer rota pode ser acessada por qualquer usuário na rede
- Ações destrutivas sem confirmação na UI — risco concreto de perda de dados por clique acidental
- Migrações de banco sem versionamento — estado do schema desconhecido e irrecuperável após falha

**Bloqueadores para a Fase H (automações WhatsApp/Twilio):**
1. **SEC-03** — Sem autenticação: um endpoint de webhook Twilio chegando a uma app sem login é inaceitável
2. **ARCH-02** — Migrações inline sem versionamento: Fase H exige novas tabelas/colunas; qualquer falha de migração derruba o serviço em produção sem rollback
3. **SEC-01 + DB-C01** — Secret key e senha SMTP hardcoded/exposta: a Fase H traz tráfego de rede adicional e maior superfície de ataque

---

## 2. Débitos de Sistema (validado por @architect)

| ID | Débito | Área | Severidade | Esforço Est. (h) | Prioridade |
|----|--------|------|-----------|-----------------|------------|
| SEC-01 | Secret key de sessão Flask hardcoded em texto plano (app.py ln 38) | Segurança | CRITICO | 1 | P1 |
| SEC-02 | Senha SMTP armazenada em texto plano no SQLite (tabela config_email) | Segurança | CRITICO | 3 | P1 |
| SEC-03 | Ausência total de autenticação/autorização em todas as rotas | Segurança | CRITICO | 6 | P1 |
| SEC-04 | Pickle para persistência de estado — risco de deserialização arbitrária | Segurança | CRITICO | 4 | P1 |
| ARCH-01 | Dois arquivos inadimplencia.db (produção C:MATINE + repo BASE DE DADOS) sem documentação de qual é canônico | Arquitetura | ALTO | 2 | P1 |
| ARCH-02 | init_db() com 163 linhas de migrações acumulativas sem controle de versão | Arquitetura | ALTO | 5 | P1 |
| ARCH-03 | Acoplamento ao Windows via os.startfile() — bloqueia futuros deploys não-Windows | Arquitetura | ALTO | 2 | P2 |
| ARCH-04 | app.py monolítico com 970+ linhas sem separação de camadas (rotas + lógica de negócio misturados) | Arquitetura | ALTO | 12 | P2 |
| QUAL-01 | Zero testes automatizados para a aplicação Flask | Qualidade | ALTO | 16 | P2 |
| QUAL-02 | Montagem de e-mail MIME duplicada em dois locais em app.py (ln 718 e 899) | Qualidade | ALTO | 2 | P2 |
| CFG-01 | Dois requirements.txt com versões conflitantes (raiz vs 06_APP/) | Config | MEDIO | 1 | P2 |
| CFG-02 | Path Python hardcoded para usuário Lorena no launcher .bat | Config | MEDIO | 1 | P2 |
| QUAL-03 | Dead code: gerar_txt() e gerar_xlsx() legadas em processing.py | Qualidade | MEDIO | 1 | P3 |
| QUAL-04 | Ausência de índices no SQLite — detalhado em débitos de Database | Qualidade | MEDIO | — | ver DB |
| QUAL-05 | detectar_tratamento() — heurística de gênero frágil com excessões hardcoded | Qualidade | MEDIO | 2 | P3 |
| QUAL-06 | Validação de upload somente por extensão (arquivo corrompido com extensão válida falha silenciosamente) | Qualidade | MEDIO | 2 | P3 |
| QUAL-07 | _carregar_estado() silencia erros de corrupção de pickle sem log ou alerta | Qualidade | MEDIO | 1 | P2 |
| DOC-01 | README.md desatualizado — descreve app Tkinter legada, não Flask atual | Documentação | BAIXO | 2 | P3 |
| DOC-02 | Imports não utilizados em app.py (json, shutil) | Documentação | BAIXO | 0.5 | P3 |
| DOC-03 | get_templates() em database.py provavelmente dead code | Documentação | BAIXO | 0.5 | P3 |
| PERF-01 | Template lookup em loop .iterrows() — aceitável agora, monitorar em Fase H | Performance | BAIXO | 3 | P3 |
| PERF-02 | Bootstrap e Bootstrap Icons via CDN sem fallback offline | Performance | BAIXO | 2 | P3 |

**Subtotal Sistema:** 22 débitos | Críticos: 4 | Altos: 6 | Médios: 6 | Baixos: 6
**Esforço estimado Sistema:** ~70h

---

## 3. Débitos de Database

> PENDENTE: Revisão do @data-engineer — estimativas sujeitas a ajuste

| ID | Débito | Severidade | Esforço Est. (h) | Prioridade |
|----|--------|-----------|-----------------|------------|
| DB-C01 | Senha SMTP armazenada em texto plano na coluna smtp_senha sem criptografia (database.py ln 362) | CRITICO | 2 | P1 |
| DB-C02 | Ausência total de foreign key constraints + PRAGMA foreign_keys nunca ativado — dados orfãos sem cascading delete | CRITICO | 3 | P1 |
| DB-A01 | Schema sem versionamento formal — migrações inline em init_db() sem tabela schema_migrations nem rollback | ALTO | 4 | P1 |
| DB-A02 | get_envios_hoje() usa LIKE em campo TEXT data_envio — full scan sem índice (database.py ln 335) | ALTO | 1 | P2 |
| DB-A03 | Ausência de índices em coluna empresa em todas as tabelas operacionais — full scan em toda query | ALTO | 1 | P2 |
| DB-A04 | salvar_base() usa duas conexões separadas sem transação atômica — risco de inconsistência em falha parcial | ALTO | 2 | P2 |
| DB-M01 | Datas armazenadas como TEXT DD/MM/YYYY — impossível ordenar ou filtrar por data nativamente no SQLite | MEDIO | 4 | P2 |
| DB-M02 | Valores monetários como REAL (ponto flutuante) — erros de arredondamento em somas agregadas | MEDIO | 3 | P3 |
| DB-M03 | Sem tabela empresas — discriminador empresa é TEXT livre sem validação no banco | MEDIO | 2 | P2 |
| DB-M04 | incrementar_cobrancas() usa executemany sem tratamento de excessão contextualizado | MEDIO | 1 | P2 |
| DB-M05 | envios.template_titulo referencia template por TEXT em vez de id INTEGER — rastreabilidade quebrada se template for renomeado | MEDIO | 3 | P2 |
| DB-B01 | get_conn() não habilita WAL mode — sem leituras concorrentes durante escritas | BAIXO | 0.25 | P3 |
| DB-B02 | Ausência de estratégia de backup documentada para o arquivo SQLite único | BAIXO | 2 | P2 |
| DB-B03 | Colunas booleanas ativo e smtp_tls sem CHECK (ativo IN (0, 1)) — aceita qualquer INTEGER | BAIXO | 0.5 | P3 |

**Subtotal Database:** 14 débitos | Críticos: 2 | Altos: 4 | Médios: 5 | Baixos: 3
**Esforço estimado Database:** ~29h (sujeito a revisão de @data-engineer)

---

## 4. Débitos de Frontend/UX

> PENDENTE: Revisão do @ux-design-expert — estimativas sujeitas a ajuste

| ID | Débito | Severidade | Esforço Est. (h) | Prioridade |
|----|--------|-----------|-----------------|------------|
| UX-CRIT-01 | Ausência total de loading state em ações síncronas longas (Consolidar, Gerar Relatórios, Atualizar Base, Upload) — risco de duplo clique e processamento duplicado | CRITICO | 4 | P1 |
| UX-CRIT-02 | Comparar e Atualizar Base executa imediatamente sem confirmação — ação modifica o SQLite permanentemente | CRITICO | 2 | P1 |
| UX-CRIT-03 | Limpar Sessão executa como link GET sem confirmação — perda total da consolidação por clique acidental | CRITICO | 1 | P1 |
| UX-HIGH-01 | Encoding quebrado no layout.html — título da aba exibe caracteres corrompidos (Windows-1252 vs UTF-8) | ALTO | 1 | P1 |
| UX-HIGH-02 | Bug de cor: Novos Inadimplentes e Régua recebem a mesma classe table-cat-a em resultado.html — categorias indistinguíveis | ALTO | 1 | P1 |
| UX-HIGH-03 | Sidebar fixa sem comportamento responsivo — em tablets conteúdo espremido, em mobile a sidebar bloqueia tudo | ALTO | 6 | P2 |
| UX-HIGH-04 | Navegação por hash em configuracoes.html pode não funcionar na carga inicial | ALTO | 1 | P2 |
| UX-HIGH-05 | Tabela de base.html com 13 colunas sem priorização — scroll horizontal intenso em 1366px (resolução padrão corporativa) | ALTO | 3 | P2 |
| UX-HIGH-06 | Feedback de Gerar Relatórios depende exclusivamente do flash message — sem confirmação visual de sucesso na tela | ALTO | 2 | P2 |
| UX-MED-01 | Badges de categoria inconsistentes entre resultado.html e wizard_whatsapp.html — design system fragmentado | MEDIO | 2 | P2 |
| UX-MED-02 | Input de upload sem preview do arquivo selecionado nem validação client-side de tipo | MEDIO | 2 | P2 |
| UX-MED-03 | title estático — em abas múltiplas do browser impossível distinguir qual tela está aberta | MEDIO | 1 | P2 |
| UX-MED-04 | Wizard Marcar Todos Enviados sem feedback granular (sem contagem de quantos foram processados) | MEDIO | 1 | P2 |
| UX-MED-05 | Modal de edição de template sem preview ao vivo das variáveis — inconsistente com a listagem | MEDIO | 3 | P3 |
| UX-MED-06 | Filtro de busca em resultado.html não busca por telefone — inconsistente com wizard_whatsapp.html | MEDIO | 1 | P3 |
| UX-MED-07 | Tooltip de e-mail via title nativo — não acessível em touch nem via leitor de tela | MEDIO | 1 | P3 |
| UX-LOW-01 | Sem atalhos de teclado para o fluxo diário (Upload, Consolidar, Gerar, Enviar) | BAIXO | 4 | P3 |
| UX-LOW-02 | Sem paginação ou virtualização nas tabelas — degradação de performance com volume alto de inadimplentes | BAIXO | 8 | P3 |
| UX-LOW-03 | Cards de mensagem em configuracoes.html sem indicação de ordem de aplicação na régua | BAIXO | 1 | P3 |
| UX-LOW-04 | Topbar não exibe nome da empresa ativa em texto — empresa indicada apenas pela opacidade do logo | BAIXO | 1 | P3 |
| UX-LOW-05 | Abrir Relatórios sem feedback se a pasta do dia não existir | BAIXO | 1 | P3 |

**Subtotal Frontend/UX:** 21 débitos | Críticos: 3 | Altos: 6 | Médios: 7 | Baixos: 5
**Esforço estimado Frontend/UX:** ~46h (sujeito a revisão de @ux-design-expert)

---

## 5. Matriz de Priorização Preliminar (Top 10)

| Rank | ID | Débito | Severidade | Área | Esforço (h) | Justificativa |
|------|----|--------|-----------|------|------------|---------------|
| 1 | SEC-01 | Secret key hardcoded em app.py | CRITICO | Segurança | 1 | Máximo impacto com mínimo esforço — 1 linha resolve comprometimento total de sessão |
| 2 | UX-CRIT-02 | Atualizar Base sem confirmação | CRITICO | UX | 2 | Ação irreversível no SQLite de produção — risco ativo de perda de dados em operação diária |
| 3 | UX-CRIT-01 | Loading state ausente nas ações principais | CRITICO | UX | 4 | Duplo clique em Consolidar pode corromper dados ou gerar inconsistências |
| 4 | UX-CRIT-03 | Limpar Sessão sem confirmação | CRITICO | UX | 1 | Link GET por clique acidental apaga horas de trabalho de consolidação |
| 5 | DB-C01 / SEC-02 | Senha SMTP em texto plano | CRITICO | DB/Segurança | 3 | Credencial corporativa exposta — qualquer backup ou cópia a expõe |
| 6 | DB-C02 | Foreign keys não declaradas nem ativadas | CRITICO | Database | 3 | limpar_base() apaga sem propagar para envios — histórico fica orfão silenciosamente |
| 7 | DB-A01 / ARCH-02 | Migrações sem versionamento | ALTO | DB/Arquitetura | 9 | Bloqueador direto para Fase H — novas colunas sem controle podem corromper o banco em produção |
| 8 | SEC-03 | Sem autenticação nas rotas | CRITICO | Segurança | 6 | Bloqueador absoluto para Fase H — webhook Twilio sem auth é vetor de ataque direto |
| 9 | UX-HIGH-01 | Encoding quebrado no título | ALTO | UX | 1 | Afeta todas as páginas — problema visível em 100% das interações; corrigível em minutos |
| 10 | UX-HIGH-02 | Cores iguais para categorias distintas em resultado.html | ALTO | UX | 1 | Bug visual que impede distinção de Novos vs Régua na tela central do fluxo |

**Esforço total Top 10:** ~31h
**Nota:** Os ranks 7 e 8 são bloqueadores da Fase H e devem ser endereçados em conjunto.

---

## 6. Dependências entre Débitos

SEC-01 (secret key) deve ser resolvido ANTES de qualquer deploy com acesso em rede.

SEC-03 (autenticação) deve ser resolvido ANTES da Fase H (webhooks Twilio).

DB-A01 (schema_migrations) DEVE ser implementado ANTES de qualquer alteração de schema:
- DB-C02 (FK constraints) depende de DB-A01
- DB-M01 (datas ISO 8601) depende de DB-A01 — requer migração de dados
- DB-M02 (monetário em centavos) depende de DB-A01 — requer migração de dados
- DB-M03 (tabela empresas) depende de DB-A01
- DB-M05 (template_id em envios) depende de DB-A01

SEC-04 (remover pickle) pode ser resolvido junto com QUAL-07 (sem estado pickle, sem corrupção silenciosa).

ARCH-02 (refatorar init_db) pode incorporar na mesma passagem: DB-A02 (índice envios data), DB-A03 (índices empresa), DB-B01 (WAL mode).

ARCH-04 (decompor app.py) desbloqueia: QUAL-01 (testes — muito mais viável com camadas separadas), QUAL-02 (e-mail duplicado — resolve ao extrair email_service.py).

UX-CRIT-01 (loading states) resolve junto com UX-HIGH-06 (feedback de gerar relatórios).

UX-MED-01 (design system badges) resolve junto com UX-HIGH-02 (bug cor tabela).

**Regra crítica:** Executar qualquer migração de schema (DB-C02, DB-M01 a M05) sem antes implementar DB-A01 seria repetir exatamente o padrão que gerou o problema atual.

---

## 7. Perguntas para @data-engineer

**Q-DB-01 — Estratégia de migração do schema:**
O init_db() tem 163 linhas de migrações de 7 fases. Alembic para SQLite em app mono-arquivo localhost tem overhead justificável neste contexto? Ou uma tabela schema_migrations simples com scripts numerados resolve com menor fricção operacional? Qual a complexidade real de migrar os dados existentes ao adotar a nova abordagem?

**Q-DB-02 — Migração de datas (DB-M01) — impacto nos dados históricos:**
Converter DD/MM/YYYY para ISO 8601 requer UPDATE em massa em múltiplas colunas de múltiplas tabelas. Qual o volume atual de registros em produção? Existe risco de dados com formato inconsistente que possam quebrar o UPDATE em massa?

**Q-DB-03 — Criptografia da senha SMTP (DB-C01):**
Para criptografar smtp_senha com cryptography.fernet, a chave precisa ficar fora do banco. Considerando que o app roda via .bat no Windows, qual o mecanismo mais robusto e operacionalmente simples? Windows DPAPI via pywin32 é viável? Ou o módulo keyring do Python é suficiente para este contexto?

**Q-DB-04 — Banco canônico (ARCH-01):**
Confirmado que BASE DE DADOS/inadimplencia.db no repositório é cópia antiga de desenvolvimento e C:MATINE/banco/inadimplencia.db é o banco de produção? Se sim, o arquivo do repositório deve ser removido via .gitignore? Há dados relevantes que precisam ser preservados?

**Q-DB-05 — Pickle vs alternativa para estado de consolidação (SEC-04):**
O pickle persiste um pd.DataFrame por empresa. Com a Fase H trazendo automações via agendador, duas execuções simultâneas leriam o mesmo .pkl. Migrar para tabela sessoes no SQLite com DataFrame serializado em JSON é viável sem impacto no fluxo da Luana? Ou o estado deve ser efêmero (recalculado sob demanda)?

---

## 8. Perguntas para @ux-design-expert

**Q-UX-01 — Wizard WhatsApp — modo manual vs automático (Fase H):**
O wizard atual é totalmente manual. A Fase H prevê envio automático via WAHA/Twilio. O redesenho deve manter o modo manual como fallback ou o automático substitui completamente? Se ambos coexistirem, qual a forma mais clara de apresentar os dois modos para a Luana (não técnica)?

**Q-UX-02 — Indicador visual de empresa ativa — risco de contexto errado:**
O maior risco operacional é enviar cobranças da empresa errada. Além do toggle atual, quais indicadores visuais permanentes são mais eficazes? Cor da topbar por empresa? Banner de alerta persistente? A mudança de empresa deve exigir confirmação explícita?

**Q-UX-03 — configuracoes.html com 29KB e 5 abas — impacto na divisão:**
Dividir em sub-rotas resolve o peso mas quebra a navegação por hash atual e os sublinks da sidebar. Como redesenhar minimizando o impacto no fluxo da Luana, que já conhece a estrutura atual?

**Q-UX-04 — Mensagens de erro para operadora não técnica:**
Quais são os erros mais frequentes que a Luana já reportou na operação atual? Quais as 5 mensagens de erro mais urgentes para traduzir para linguagem operacional (ex: O arquivo de Vencidos não possui a coluna CPF esperada — verifique se exportou do Synapta)?

**Q-UX-05 — Volume de dados e virtualização de tabelas (UX-LOW-02):**
UX-LOW-02 está classificado como baixo assumindo volume gerenciável. Qual o volume real de inadimplentes por empresa em produção atualmente? Acima de ~300 linhas sem virtualização a filtragem fica visivelmente lenta em hardware corporativo típico. Esse limiar já foi atingido?

---

## Apêndice: Consolidação de Fontes

| Fonte | Débitos Originados | Documento |
|-------|-------------------|-----------|
| @architect — system-architecture.md | SEC-01 a 04, ARCH-01 a 04, QUAL-01 a 07, CFG-01 a 02, DOC-01 a 03, PERF-01 a 02 | docs/architecture/system-architecture.md |
| @data-engineer — SCHEMA.md + DB-AUDIT.md | DB-C01 a 02, DB-A01 a 04, DB-M01 a 05, DB-B01 a 03 | docs/database/SCHEMA.md + DB-AUDIT.md |
| @ux-design-expert — frontend-spec.md | UX-CRIT-01 a 03, UX-HIGH-01 a 06, UX-MED-01 a 07, UX-LOW-01 a 05 | docs/frontend/frontend-spec.md |

**Total de débitos:** 43
**Esforço total estimado (sujeito a revisão):** ~145h

---

*Documento gerado por Aria (@architect) — Brownfield Discovery Fase 4*
*Próximos passos:*
*  Fase 5: @data-engineer revisa Seção 3 e responde Seção 7*
*  Fase 6: @ux-design-expert revisa Seção 4 e responde Seção 8*
*  Fase 7: @qa executa QA Gate (APPROVED / NEEDS WORK)*
*  Fase 8: Documento final technical-debt-assessment.md*
