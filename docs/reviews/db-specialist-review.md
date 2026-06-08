# Database Specialist Review
**Revisor:** @data-engineer (Dara)
**Data:** 04/06/2026
**DRAFT revisado:** docs/prd/technical-debt-DRAFT.md (Secao 3)
**Base:** DB-AUDIT.md (Fase 2) + SCHEMA.md + 06_APP/database.py (releitura direta)

---

## 1. Debitos Validados

| ID | Debito | Severidade Original | Severidade Revisada | Horas Est. (revisadas) | Prioridade | Notas |
|----|--------|---------------------|---------------------|------------------------|------------|-------|
| DB-C01 | Senha SMTP em texto plano na coluna smtp_senha (database.py ln 513-528) | CRITICO | CRITICO | 3h | P1 | Estimativa original de 2h subestimada. Criptografar requer: (1) gerar e armazenar chave fora do DB, (2) migrar registro existente em config_email, (3) atualizar get_config_email para descriptografar, (4) testar com SMTP real. 3h e realista. |
| DB-C02 | Ausencia total de foreign key constraints + PRAGMA foreign_keys nunca ativado | CRITICO | CRITICO | 3h | P1 | Confirmado. get_conn() (ln 129-132) sem pragma. Dados orfaos existentes podem violar constraints ao ativa-las -- requer limpeza previa. |
| DB-A01 | Schema sem versionamento formal -- migracoes inline em init_db() sem schema_migrations nem rollback | ALTO | ALTO | 5h | P1 | Estimativa revisada de 4h para 5h. init_db() tem 163 linhas (ln 135-295) com 7 fases misturadas. Separar em funcoes atomicas + criar schema_migrations + testar idempotencia = 5h minimo. |
| DB-A02 | get_envios_hoje() usa LIKE em campo TEXT data_envio -- full scan sem indice (ln 495-508) | ALTO | ALTO | 1h | P2 | Confirmado. Com crescimento do historico sera o primeiro gargalo de performance visivel. Indice composto em (empresa, data_envio) resolve. |
| DB-A03 | Ausencia de indices em coluna empresa em todas as tabelas operacionais | ALTO | ALTO | 1h | P2 | Confirmado: nenhum CREATE INDEX em todo o database.py. 5 tabelas, todas filtradas por empresa. Com 2 tenants, cada query descarta ~50% dos registros via full scan. |
| DB-A04 | salvar_base() usa duas conexoes separadas sem transacao atomica (ln 374-449) | ALTO | ALTO | 2h | P2 | Confirmado. Duas conexoes: leitura ln 378, escritas ln 393. Loop de UPSERT (ln 397-432) sem try/except. Falha no registro N deixa N-1 gravados sem historico_atualizacoes. |
| DB-M01 | Datas armazenadas como TEXT DD/MM/YYYY | MEDIO | MEDIO | 5h | P2 | Estimativa revisada de 4h para 5h. 5 colunas em 3 tabelas. Pelo menos 6 ocorrencias de strftime no codigo a atualizar. Risco de formatos inconsistentes em ultimo_vencimento (ver Q-DB-02). |
| DB-M02 | Valores monetarios como REAL (ponto flutuante) | MEDIO | MEDIO | 3h | P3 | Confirmado. Coluna total REAL recebe float(row[Total]) (ln 424). Conversao para INTEGER em centavos requer atualizar salvar_base, carregar_base e migrar dados. |
| DB-M03 | Sem tabela empresas -- discriminador empresa e TEXT livre | MEDIO | MEDIO | 2h | P2 | Confirmado. EMPRESAS apenas como constante Python (ln 13). Criar tabela + FK nas 5 tabelas + migrar = 2h. |
| DB-M04 | incrementar_cobrancas() usa executemany sem tratamento de excecao contextualizado (ln 340-349) | MEDIO | BAIXO | 0.5h | P3 | SEVERIDADE REBAIXADA. executemany dentro de with get_conn() e transacional por default no sqlite3 Python -- atomicidade preservada. Gap e apenas de observabilidade: traceback sem contexto do CPF que falhou. |
| DB-M05 | envios.template_titulo referencia template por TEXT em vez de id INTEGER | MEDIO | MEDIO | 3h | P2 | Confirmado: registrar_envio (ln 485-492) grava template_titulo TEXT. Renomear template quebra rastreabilidade historica. 3h para adicionar template_id, popular via JOIN e deprecar template_titulo. |
| DB-B01 | get_conn() nao habilita WAL mode | BAIXO | BAIXO | 0.25h | P3 | Confirmado. get_conn() (ln 129-132) sem PRAGMA. 2 linhas. 15min. ATENCAO: BLOQUEADOR para Fase H (agendador concorrente). |
| DB-B02 | Ausencia de estrategia de backup para o SQLite unico | BAIXO | BAIXO | 2h | P2 | Confirmado. Nenhuma referencia a backup em todo o codebase. DB em C:\MATINE\banco\ hardcoded (ln 11). Falha de disco = perda total. |
| DB-B03 | Colunas booleanas ativo e smtp_tls sem CHECK constraint | BAIXO | BAIXO | 0.5h | P3 | Confirmado. ativo INTEGER DEFAULT 1 em templates e smtp_tls INTEGER DEFAULT 1 em config_email aceitam qualquer INTEGER. CHECK via migracao = 30min. |
