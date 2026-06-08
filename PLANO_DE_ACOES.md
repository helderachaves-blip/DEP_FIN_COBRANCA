# PLANO DE AÇÕES - MAT-INE INADIMPLÊNCIA 2026

**Período:** 19 a 25 de Maio de 2026  
**Responsável:** EDILVO  
**Email:** gerente@ineprotec.com.br

---

## RESUMO EXECUTIVO

Este projeto estrutura o processo de recebimentos através do mapeamento de plataformas de pagamento, análise de inadimplência e implementação de automações para cobranças, com execução em 1 semana.

### Objetivos

| MAPEAMENTO | AUTOMAÇÃO |
|-----------|-----------|
| • Plataformas de pagamento | • Régua de cobrança automática |
| • Tipos de pagamentos | • Avisos automáticos |
| • Taxa de inadimplência | • Negativação de nomes |
| • Melhores dias de pagamento | • Dashboard de métricas |

---

## PLANO DE EXECUÇÃO

### FASE 1: DIAGNÓSTICO E MAPEAMENTO (Dias 1-2)

Análise completa do processo atual de recebimentos.

| # | TAREFA | DESCRIÇÃO | RESPONSÁVEL | PRAZO |
|---|--------|-----------|-------------|-------|
| 1.1 | Consolidar plataformas de pagamento | Documentar todas as plataformas, integrações e fluxos de pagamento atualmente utilizados | EDILVO | Dia 1 |
| 1.2 | Analisar dados de inadimplência | Extrair relatórios históricos, taxas por período, padrões e desvios | Analista | Dia 1 |
| 1.3 | Mapear processos de cobrança | Detalhar fluxo atual: avisos, prazos, canais de contato, responsabilidades | Analista | Dia 2 |
| 1.4 | Identificar melhores dias | Analisar padrão de recebimentos por dia da semana, períodos do mês | Analista | Dia 2 |

**Entrega esperada:** Relatório de diagnóstico com mapeamento completo

---

### FASE 2: DESIGN DA SOLUÇÃO (Dia 3)

Planejamento técnico e operacional da automação.

| # | TAREFA | DESCRIÇÃO | RESPONSÁVEL | PRAZO |
|---|--------|-----------|-------------|-------|
| 2.1 | Definir régua de cobrança | Sequência de avisos: 5d antes, 10d, 15d e 30d (negativação) | EDILVO | Dia 3 |
| 2.2 | Especificar integrações | Definir quais plataformas se integram com a solução automática | Desenvolvimento | Dia 3 |
| 2.3 | Planejar fluxo de negativação | Critérios, conformidade legal e processo de inclusão/negativação | Compliance | Dia 3 |

**Entrega esperada:** Especificação técnica aprovada da solução

---

### FASE 3: IMPLEMENTAÇÃO (Dias 4-6)

Desenvolvimento e testes da solução de automação.

| # | TAREFA | DESCRIÇÃO | RESPONSÁVEL | PRAZO |
|---|--------|-----------|-------------|-------|
| 3.1 | Desenvolver automações | Scripts/workflows para avisos automáticos via email/SMS/API | Desenvolvimento | Dia 4-5 |
| 3.2 | Testar fluxos | QA completo de todos os processos: avisos, cobranças, negativações | QA | Dia 5-6 |
| 3.3 | Configurar dashboard | Métricas de inadimplência, recebimentos, taxas de sucesso | Desenvolvimento | Dia 4-5 |

**Entrega esperada:** Sistema de automação funcional e testado

---

### FASE 4: VALIDAÇÃO E DEPLOY (Dia 7)

Aprovação final e colocação em produção.

| # | TAREFA | DESCRIÇÃO | RESPONSÁVEL | PRAZO |
|---|--------|-----------|-------------|-------|
| 4.1 | Validação final | Apresentação com stakeholders, testes em piloto | EDILVO | Dia 7 |
| 4.2 | Deploy | Colocar automações em ambiente de produção | Desenvolvimento | Dia 7 |
| 4.3 | Treinamento | Documentação e treino da equipe de cobranças | EDILVO | Dia 7 |

**Entrega esperada:** Sistema em produção, documentado e equipe treinada

---

## CRONOGRAMA VISUAL

```
SEMANA DE EXECUÇÃO - 19/05 a 25/05/2026

Atividade                    | Seg | Ter | Qua | Qui | Sex | Sab | Dom
-----------------------------|-----|-----|-----|-----|-----|-----|-----
Diagnóstico e Mapeamento    |  ✓  |  ✓  |     |     |     |     |
Design da Solução           |     |     |  ✓  |     |     |     |
Implementação               |     |     |     |  ✓  |  ✓  |     |
Testes e Validação          |     |     |     |     |  ✓  |  ✓  |
Deploy e Treinamento        |     |     |     |     |     |  ✓  |
```

---

## RÉGUA DE COBRANÇA RECOMENDADA

Esta é a sequência automática de contatos com devedores:

| Evento | Dias | Ação | Canal |
|--------|------|------|-------|
| Aviso de vencimento | -5 dias | Email/SMS lembrança | Automático |
| Primeira cobrança | +10 dias | Aviso de atraso | Email/SMS/WhatsApp |
| Segunda cobrança | +15 dias | Cobrança intensiva | Telefone + Email |
| Negativação | +30 dias | Inclusão em órgãos | Automático + Manual |

---

## DEPENDÊNCIAS CRÍTICAS

✓ **Fase 1 → Fase 2:** Diagnóstico deve estar 100% concluído  
✓ **Fase 2 → Fase 3:** Design deve ser aprovado por stakeholders  
✓ **Fase 3 → Fase 4:** Testes completos e sem erros críticos  
✓ **Fase 4 → Produção:** Validação final aprovada por EDILVO  

---

## RESPONSÁVEIS

| Função | Responsável | E-mail | Função |
|--------|-------------|--------|--------|
| Gerente Projeto | EDILVO | gerente@ineprotec.com.br | Coordenação geral |
| Analista | [A definir] | | Diagnóstico e análise |
| Desenvolvimento | [A definir] | | Implementação técnica |
| QA | [A definir] | | Testes |
| Compliance | [A definir] | | Conformidade legal |

---

## OBSERVAÇÕES IMPORTANTES

### O que vocês já têm documentado
✓ Lista de plataformas de pagamento  
✓ Dados de inadimplência  
✓ Processos de cobrança atual  

### O que falta
- [ ] Estruturação técnica da automação
- [ ] Integração de APIs
- [ ] Dashboard de métricas
- [ ] Documentação e treinamento

### Próximos Passos
1. **Hoje (Dia 1):** Confirmar equipe responsável por cada fase
2. **Hoje (Dia 1):** Iniciar FASE 1 com coleta de dados
3. **Dia 3:** Revisar progresso e ajustar cronograma se necessário
4. **Dia 7:** Apresentação final com resultado

---

## MATRIZ DE DECISÃO

### Caso haja atrasos em uma fase, priorizamos:
1. **Mapeamento completo** - sem dados não temos base para automação
2. **Design validado** - evita retrabalho na implementação
3. **Implementação robusta** - qualidade > velocidade
4. **Testes rigorosos** - erros em produção são custosos

---

**Documento criado em:** 19/05/2026  
**Próxima revisão:** 22/05/2026 (fim da Fase 2)
