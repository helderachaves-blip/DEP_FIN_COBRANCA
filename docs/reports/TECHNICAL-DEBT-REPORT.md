# Relatorio Executivo — Debitos Tecnicos
## MAT-INE Inadimplencia 2026

**Data:** 04/06/2026
**Para:** Edilvo (Gerente) · Helder (TI)
**Preparado por:** Alex (@analyst) — Brownfield Discovery Fase 9
**Fonte:** Technical Debt Assessment Final (docs/prd/technical-debt-assessment.md)

---

## O que e Debito Tecnico?

Debito tecnico e o conjunto de problemas de construcao no sistema atual que nao impedem o funcionamento hoje, mas que:
- Aumentam o risco de falhas e perda de dados
- Tornam cada nova funcionalidade mais cara e demorada de implementar
- Podem virar problemas criticos com o crescimento do uso

Este relatorio descreve o que foi encontrado no sistema MAT-INE apos uma auditoria tecnica completa (8 especialistas, 4 dias de analise).

---

## 1. Situacao Atual em Numeros

| | |
|-|-|
| **Problemas encontrados** | 58 ao total |
| **Criticos (risco imediato)** | 10 |
| **Altos (risco em semanas)** | 16 |
| **Medios (risco em meses)** | 17 |
| **Baixos (melhorias futuras)** | 15 |
| **Horas estimadas para resolver tudo** | ~147h (~18 dias de trabalho) |
| **Horas para resolver os criticos** | ~30h (~4 dias) |

---

## 2. Os 3 Riscos Mais Urgentes (Hoje)

### Risco 1 — Dados Sensiveis Expostos

**O que e:** A senha do e-mail corporativo (Gmail) esta armazenada sem protecao no banco de dados do sistema. A chave de seguranca do servidor tambem esta exposta no codigo-fonte.

**O que pode acontecer:** Qualquer pessoa que acesse o arquivo do banco de dados — inclusive em um backup ou copia acidental — pode ver a senha do e-mail. Isso da acesso a toda a caixa de entrada corporativa.

**Quanto custa resolver:** 4 horas de desenvolvimento.

---

### Risco 2 — Acoes Sem Pedido de Confirmacao

**O que e:** O botao "Comparar e Atualizar Base" e o link "Limpar Sessao" executam imediatamente, sem pedir confirmacao. Um clique errado da Luana pode:
- Apagar horas de trabalho de consolidacao (Limpar Sessao)
- Modificar permanentemente o banco de inadimplentes (Atualizar Base)

**O que pode acontecer:** Perda de dados em operacao diaria. Ja acontece com botoes sem trava em outros sistemas similares.

**Quanto custa resolver:** 3 horas de desenvolvimento.

---

### Risco 3 — Sistema sem Trava de Acesso

**O que e:** Qualquer pessoa na rede interna que saiba o endereco IP do computador da Luana pode acessar o sistema sem usuario nem senha.

**O que pode acontecer:** Qualquer funcionario ou visitante na rede pode ver, alterar ou apagar dados de inadimplentes. Isso tambem e um requisito para a Fase H (integracao WhatsApp) — sem autenticacao, o webhook de mensagens automaticas fica exposto.

**Quanto custa resolver:** 6 horas de desenvolvimento.

---

## 3. O que Bloqueia a Fase H (WhatsApp Automatico)

A Fase H — que automatizaria o envio de mensagens via WhatsApp e integraria o Kommo CRM — esta BLOQUEADA por 3 problemas:

| Bloqueador | Problema | Custo para resolver |
|-----------|---------|-------------------|
| Sem autenticacao | Um sistema sem login nao pode receber mensagens automaticas de fora com seguranca | 6h |
| Banco sem controle de versao | Novas tabelas necessarias para a Fase H podem corromper o banco existente sem como voltar atras | 10h |
| Senhas expostas | Com mais trafego externo na Fase H, a superficie de ataque aumenta muito | 4h |

**Total para desbloquear Fase H: ~20h (~2,5 dias de trabalho)**

---

## 4. Plano de Resolucao Recomendado

### Sprint Zero — Pré-Fase H (~30h / 4 semanas)
**Objetivo:** Resolver todos os 10 criticos e preparar o terreno para a Fase H.

| Semana | O que sera feito | Horas |
|--------|-----------------|-------|
| 1 | Corrigir encoding, cores, confirmacoes de clique, indicador de empresa | 8h |
| 2 | Loading screens, modal de Atualizar Base, proteger senha do e-mail | 8h |
| 3 | Controle de versao do banco + indices de performance | 12h |
| 4 | Sistema de login (usuario unico) | 6h |
| **Total** | | **~34h** |

### Sprint 1 — Estabilizacao (~60h / 7 semanas)
Refatorar o codigo principal, adicionar testes automatizados, responsividade em tablet.

### Sprint 2 — Qualidade Restante (~53h / 6 semanas)
Melhorias de UX, backup automatico, resolucao dos debitos de medio e baixo impacto.

---

## 5. O que o Sistema Faz Bem (Nao e So Problema)

A auditoria tambem identificou pontos positivos:

- **Fluxo de envio de mensagens:** Feedback visual excelente (linha fica verde, progresso atualiza em tempo real, toast confirma cada acao)
- **Estados vazios tratados:** Cada tela tem mensagem clara quando nao ha dados
- **Separacao de empresas:** Ineprotec e Matricula EAD corretamente isoladas
- **Geracao de relatorios:** Pastas organizadas por data e empresa funcionam bem
- **Acessibilidade basica:** Estrutura HTML semantica com roles e aria-labels presentes
- **Logs:** Sistema de log ativo registrando operacoes

O sistema foi bem construido para o tamanho e complexidade do problema. Os debitos encontrados sao naturais de um sistema que evoluiu rapido em resposta a demandas reais.

---

## 6. Custo de Nao Resolver

Se os debitos criticos nao forem resolvidos antes da Fase H:

| Consequencia | Probabilidade |
|-------------|--------------|
| Senha de e-mail comprometida em backup | Media |
| Perda de dados por clique acidental (Luana) | Alta — ja reportada como risco diario |
| Sistema invadido via rede interna | Baixa agora, Alta na Fase H |
| Banco corrompido sem como voltar atras | Media — uma falha de migracao resolve isso |
| Atraso da Fase H por retrabaho | Muito Alta — sem resolver os bloqueadores, a Fase H nao pode comecar |

---

## 7. Resumo Executivo em Uma Pagina

O sistema MAT-INE funciona e entrega valor. Porem, para crescer com seguranca e viabilizar a automacao via WhatsApp (Fase H), e necessario resolver ~30h de debitos criticos primeiro.

O investimento de ~4 semanas de desenvolvimento tecnico resolve:
- 10 problemas criticos de seguranca e dados
- Os 3 bloqueadores da Fase H
- A experiencia da Luana no uso diario (confirmacoes de seguranca, loading screens, indicadores visuais)

Sem esse investimento, a Fase H carrega risco alto de falha e os problemas de seguranca continuam ativos.

---

*Alex (@analyst) — Brownfield Discovery Fase 9 — MAT-INE Inadimplencia 2026*
*Documento tecnico completo: docs/prd/technical-debt-assessment.md*
