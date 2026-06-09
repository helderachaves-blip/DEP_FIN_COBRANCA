# ANÁLISE: PROCESSO ATUAL vs NOVO PROCESSO AUTOMÁTICO
## MAT-INE Inadimplência 2026

---

## 📊 MAPEAMENTO DO PROCESSO ATUAL

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSO MANUAL ATUAL                         │
└─────────────────────────────────────────────────────────────────┘

PASSO 1: EXTRAÇÃO DE DADOS (⏱️ ~15-30 min manual)
  └─> Login no Synapta
  └─> Menu Vendas > Faturas
  └─> Filtro "Vencido" > Exportar para Excel
  └─> RESULTADO: Planilha com faturas vencidas
      (Sem contexto: não sabe automaticamente quantos dias está vencido)

PASSO 2: ANÁLISE MANUAL (⏱️ ~30-45 min)
  └─> Abre planilha Excel
  └─> Insere fórmula =HOJE()-[data vencimento]
  └─> Seleciona boletos com 7 dias, 15 dias, 30 dias de atraso
  └─> Cria 3 listas diferentes (uma para cada faixa)
  └─> RESULTADO: 3 planilhas com grupos de clientes

PASSO 3: VERIFICAÇÃO NO SISTEMA (⏱️ ~45-60 min)
  └─> Volta ao Synapta
  └─> Entra em CADA aluno individualmente
  └─> Verifica: quantos boletos? qual valor total? qual status?
  └─> Manualmente anota na planilha
  └─> RESULTADO: Planilha com informações do aluno

PASSO 4: ENVIO DE MENSAGENS (⏱️ ~45-90 min)
  └─> Abre WhatsApp
  └─> Copia mensagem padrão
  └─> Para CADA cliente individualmente:
      ├─> Cola mensagem
      ├─> Personaliza (nome do aluno, curso, data vencimento)
      ├─> Envia
  └─> RESULTADO: Mensagens enviadas, sem rastreamento

PASSO 5: NEGOCIAÇÃO E CRIAÇÃO DE BOLETOS (⏱️ variável, MANUAL)
  └─> Cliente responde no WhatsApp
  └─> Volta ao Synapta
  └─> Cancela boletos em aberto
  └─> Cria novos boletos
  └─> Gera PDF ou link PIX
  └─> Envia via WhatsApp
  └─> RESULTADO: Novo boleto para cliente

┌─────────────────────────────────────────────────────────────────┐
│ ⏱️  TEMPO TOTAL: 2.5 a 4 horas POR DIA
│ 📊 FREQUÊNCIA: Diária (você faz isso todo dia)
│ 👤 RESPONSÁVEL: EDILVO manualmente
│ ❌ ESCALABILIDADE: Péssima (não cresce com volume de clientes)
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔴 PROBLEMAS IDENTIFICADOS

| PROBLEMA | IMPACTO | CAUSA |
|----------|---------|-------|
| **Tempo gasto: 2.5-4h/dia** | ~120-200h/mês de trabalho manual | Sistema não é integrado |
| **Dados em Excel** | Propenso a erros, falta de histórico | Extração manual |
| **Volta ao Synapta múltiplas vezes** | Perda de tempo procurando dados | Dados espalhados |
| **WhatsApp manual** | Lento, sem rastreamento, sem padronização | Sem automação |
| **Sem rastreamento de tentativas** | Não sabe se cliente foi contatado | Sem log |
| **Sem inteligência na priorização** | Envia para todos em ordem aleatória | Sem algoritmo |
| **Manualmente volta para criar boletos** | Necessário acesso manual ao sistema | Sem fluxo automático |
| **Sem consolidação de dados** | Difícil ver padrões e métricas | Dados espalhados |

---

## 🟢 NOVO PROCESSO PROPOSTO (AUTOMATIZADO)

```
┌──────────────────────────────────────────────────────────────────┐
│                  NOVO PROCESSO AUTOMÁTICO                         │
└──────────────────────────────────────────────────────────────────┘

ETAPA 1: EXTRAÇÃO AUTOMÁTICA DE DADOS (⏱️ AUTOMÁTICO, 0% manual)
  ┌─ Trigger: Diário às 6:00 AM
  │
  ├─> Sistema automático acessa Synapta (API ou WebScraping)
  ├─> Extrai: Todas as faturas do último dia
  ├─> Processa: Calcula automaticamente HOJE() - data vencimento
  ├─> Categoriza: Separa por dias de atraso (7d, 15d, 30d, 60d)
  ├─> Valida: Verifica dados de aluno completos
  ├─> Armazena: Em banco de dados centralizado (não Excel!)
  │
  └─> RESULTADO: Dados estruturados e prontos
     ✓ Sem erros manuais
     ✓ Histórico completo
     ✓ Rastreável
     ✓ Imediato

ETAPA 2: ANÁLISE E SEGMENTAÇÃO INTELIGENTE (⏱️ AUTOMÁTICO)
  ┌─ Trigger: Após extração de dados
  │
  ├─> Sistema analisa:
  │   ├─ Dias de atraso
  │   ├─ Valor total devedor
  │   ├─ Histórico de comunicação (quando foi última tentativa)
  │   ├─ Número de boletos em aberto
  │   ├─ Se já foi negativado
  │
  ├─> Cria segmentação inteligente:
  │   ├─ GRUPO 1: 7 dias - Aviso preventivo (primeira cobrança)
  │   ├─ GRUPO 2: 15 dias - Cobrança moderada (segunda tentativa)
  │   ├─ GRUPO 3: 30 dias - Cobrança intensiva (terceira tentativa)
  │   ├─ GRUPO 4: 60 dias - Ação de negativação
  │   ├─ GRUPO 5: Já negativados - Ação de reintegração
  │
  ├─> Prioriza por:
  │   ├─ Valor (maiores primeiro)
  │   ├─ Dias de atraso (mais antigos primeiro)
  │   ├─ Tipo de cliente (novos vs recorrentes)
  │
  └─> RESULTADO: Lista inteligente e priorizada
     ✓ Sem decisões manuais
     ✓ Baseado em dados
     ✓ Otimizado para resultado

ETAPA 3: ENVIO AUTOMÁTICO DE MENSAGENS (⏱️ AUTOMÁTICO)
  ┌─ Trigger: Classificação por grupo
  │
  ├─> Para cada cliente no grupo:
  │
  │   GRUPO 1 (7 dias): AVISO PREVENTIVO
  │   ├─> Extrai dados do cliente (nome, curso, valor, vencimento)
  │   ├─> Personaliza mensagem automaticamente:
  │   │   "Olá, [NOME]. Tudo bem?
  │   │    Somos do setor financeiro do Matricula EaD.
  │   │    Lembramos que o boleto referente ao seu [CURSO]
  │   │    com vencimento em [DATA] está próximo.
  │   │    Valor: R$ [VALOR]
  │   │    [LINK_PIX_DIRETO]
  │   │    Se já realizou o pagamento, desconsidere!"
  │   ├─> Envia via WhatsApp (API WhatsApp Business)
  │   ├─> Registra: data/hora, mensagem, status de entrega
  │   └─> Aguarda resposta
  │
  │   GRUPO 2 (15 dias): COBRANÇA MODERADA
  │   ├─> Verifica se já foi contatado (antes)
  │   ├─> Aguarda X horas (ex: 48h) antes de nova tentativa
  │   ├─> Personaliza mensagem para segunda tentativa:
  │   │   "Olá, [NOME]. Sua fatura está vencida há X dias!
  │   │    Favor regularizar com urgência.
  │   │    Valor: R$ [VALOR] - Vencimento: [DATA]
  │   │    [LINK_PAGAMENTO]"
  │   ├─> Envia via WhatsApp
  │   ├─> Registra tentativa
  │   └─> Aguarda resposta
  │
  │   GRUPO 3 (30 dias): COBRANÇA INTENSIVA
  │   ├─> Envia via WhatsApp + SMS (impacto maior)
  │   ├─> Mensagem mais urgente
  │   ├─> Oferece opções de negociação automática
  │   └─> Registra tentativa
  │
  │   GRUPO 4 (60 dias): AÇÃO DE NEGATIVAÇÃO
  │   ├─> Dispara aviso de negativação (via SMS urgente)
  │   ├─> Oferece último prazo para regularização
  │   ├─> Se não pagar, dispara inclusão automática (se permitido)
  │   └─> Registra ação
  │
  └─> RESULTADO: Todos contactados automaticamente
     ✓ Padronizado
     ✓ Rastreado
     ✓ Sem erros
     ✓ Tempo: 0% manual

ETAPA 4: RASTREAMENTO E ANÁLISE (⏱️ AUTOMÁTICO, TEMPO REAL)
  ┌─ Sistema monitora:
  │
  ├─> Respostas do cliente:
  │   ├─ Se respondeu "Já paguei" → Verifica pagamento automático
  │   ├─ Se respondeu "Vou pagar agora" → Oferece link de pagamento
  │   ├─ Se respondeu "Não tenho condição" → Oferece plano de negociação
  │   ├─ Se não respondeu → Escalada para próximo grupo
  │
  ├─> Pagamento confirmado:
  │   ├─ Sistema detecta automaticamente (integrado com banco)
  │   ├─ Marca fatura como paga
  │   ├─ Para envio de mensagens
  │   ├─ Registra data de pagamento
  │
  ├─> Gera relatórios em tempo real:
  │   ├─ Quantas tentativas de contato
  │   ├─ Taxa de resposta
  │   ├─ Taxa de conversão (contato → pagamento)
  │   ├─ Tempo médio para pagamento após contato
  │   ├─ ROI da cobrança
  │
  └─> RESULTADO: Dashboard com tudo visualizado
     ✓ Gráficos em tempo real
     ✓ KPIs automáticos
     ✓ Identificação de padrões

ETAPA 5: NEGOCIAÇÃO E CRIAÇÃO DE BOLETOS (⏱️ SEMI-AUTOMÁTICO)
  ┌─ Quando cliente responde negociando:
  │
  ├─> Cliente diz: "Não consigo pagar tudo agora"
  ├─> Sistema oferece automaticamente opções de parcelamento:
  │   ├─ 2x | 3x | 4x
  │   └─ Cliente seleciona via menu interativo (WhatsApp)
  │
  ├─> Sistema automaticamente:
  │   ├─ Calcula novas parcelas
  │   ├─ Cancela boletos em aberto no Synapta (via API)
  │   ├─ Gera novos boletos no Synapta (via API)
  │   ├─ Extrai links PIX automáticos
  │   ├─ Envia nova mensagem com botões de pagamento
  │   ├─ Registra acordo no histórico
  │   └─ Marca para acompanhamento das novas parcelas
  │
  ├─> VOCÊ (Edilvo) intervém apenas em casos:
  │   ├─ Clientes que querem descontos maiores
  │   ├─ Situações excepcionais
  │   ├─ Renegociações de acordos anteriores
  │
  └─> RESULTADO: 80% de negociações automáticas
     ✓ Cliente negocia 24/7 (sem esperar você)
     ✓ Boletos criados automaticamente
     ✓ Você interfere apenas em exceções

┌──────────────────────────────────────────────────────────────────┐
│ ⏱️  TEMPO TOTAL: ~15 MINUTOS DE VOCÊ POR DIA
│    (Apenas revisar exceções e casos especiais)
│ 📊 FREQUÊNCIA: Totalmente automático (24/7)
│ 👤 RESPONSÁVEL: Sistema automático + você em exceções
│ ✅ ESCALABILIDADE: Perfeita (cresce sem limite)
│ 💰 IMPACTO: Redução de ~120h/mês = ~R$ 15.000/mês de economia
└──────────────────────────────────────────────────────────────────┘
```

---

## 📈 COMPARATIVO: ANTES vs DEPOIS

| MÉTRICA | ANTES | DEPOIS | GANHO |
|---------|-------|--------|-------|
| **Tempo manual por dia** | 2.5-4h | 15 min | **85-90% redução** |
| **Tempo manual por mês** | 120-200h | 7.5h | **~150h economia** |
| **Custo mensal do tempo** | ~R$ 15.000 | ~R$ 900 | **R$ 14.100** |
| **Taxa de contato (% clientes contatados)** | 60% (alguns escapam) | **99%** | **40% melhoria** |
| **Tempo para contato 1º vez** | 1-2 dias | **Até 2h** | **50x mais rápido** |
| **Rastreamento de tentativas** | Nenhum | **100% rastreado** | **Completo** |
| **Padronização de mensagens** | Manual (inconsistente) | **Perfeita** | **100%** |
| **Taxa de pagamento esperada** | ~70% | **85%+** | **+15% recuperação** |
| **Tempo para criar novo boleto** | 5-10 min manual | **30 seg automático** | **10x mais rápido** |
| **Escalabilidade** | Limitada (máx ~50 clientes/dia) | **Ilimitada** | **∞** |

---

## 🛠️ TECNOLOGIAS NECESSÁRIAS

### Para implementar este novo processo, vamos precisar de:

1. **Integração com Synapta** 
   - API do Synapta (se disponível) para extrair faturas
   - Ou WebScraping (se não tiver API)
   - Objetivo: Dados em tempo real, sem Excel manual

2. **Banco de Dados Centralizado**
   - Armazenar: Clientes, faturas, histórico de cobranças
   - Não será mais Excel! Será estruturado.

3. **Automação de WhatsApp**
   - API WhatsApp Business (enviado via Twilio, Waha ou similar)
   - Mensagens personalizadas automaticamente
   - Recebimento de respostas automaticamente

4. **Orquestração de Workflow**
   - Ferramentas: Make, Zapier, ou automation custom
   - Orquestrar: Extração → Análise → Envio → Rastreamento

5. **Dashboard**
   - Visualização em tempo real das cobranças
   - KPIs automáticos
   - Sem necessidade de abrir Synapta

---

## 🎯 PROPOSTA DE PRÓXIMOS PASSOS

### OPÇÃO A: Implementação Completa (Recomendado)
```
Semana 1-2: Setup técnico
  ├─ Validar API do Synapta
  ├─ Configurar WhatsApp Business
  ├─ Criar banco de dados

Semana 3-4: Desenvolvimento
  ├─ Criar automações
  ├─ Testar fluxos
  ├─ Validar com você

Semana 5: Deploy
  ├─ Colocar em produção
  ├─ Monitorar
  ├─ Ajustes finais
```

### OPÇÃO B: MVP (Mínimo Viável) - Começo Rápido
```
Semana 1: Quick Win
  ├─ Automatizar extração de dados (Synapta → Excel estruturado)
  ├─ Automatizar envio de WhatsApp (template + personalização)
  ├─ Criar rastreamento simples

Resultado: Já reduz 50% do tempo manual
Depois: Adicionar análise inteligente e negociação automática
```

---

## ❓ QUESTÕES PARA VOCÊ

Antes de começar, preciso que você responda:

1. **O Synapta tem API pública?** (Ou você teria que pedir para o fornecedor)
2. **Vocês já usam WhatsApp Business?** (Ou é WhatsApp pessoal?)
3. **Qual é o volume de clientes hoje?**
   - Quantos clientes ativos?
   - Quantos boletos por mês?
   - Quantos normalmente estão inadimplentes?
4. **Qual é o orçamento/timeline?**
   - Quer começar rapidinho (MVP)?
   - Ou faz tudo de uma vez (Completo)?
5. **Quem vai gerenciar isso depois?**
   - Você mesmo (com interface amigável)?
   - Um desenvolvedor?

---

**Próxima ação:** Você responde essas 5 questões e começamos o design da solução!

