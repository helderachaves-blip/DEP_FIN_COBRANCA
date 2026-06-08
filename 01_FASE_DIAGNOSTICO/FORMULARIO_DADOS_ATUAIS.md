# FORMULÁRIO: DADOS E PROCESSO ATUAL
## MAT-INE Inadimplência 2026

**Data:** 19/05/2026  
**Responsável:** EDILVO  
**Objetivo:** Mapear os dados que vocês têm hoje para desenhar um novo processo automático

---

## SEÇÃO 1: PLATAFORMAS DE PAGAMENTO

### 1.1 Quais plataformas vocês usam?
(Marque todas e descreva como funciona cada uma)

```
□ Cartão de Crédito
   - Qual processadora? (Rede, Cielo, Stripe, etc): _______________________
   - Qual taxa? _______________________
   - Como recebem os dados? (API, relatório exportado manualmente, etc): _______________________

□ Boleto Bancário
   - Qual banco? _______________________
   - Como rastreiam? (consulta manual, integração, relatório): _______________________
   - Qual é a taxa de sucesso (% que entra)? _______________________

□ PIX
   - Qual instituição? _______________________
   - Como recebem confirmação? _______________________
   - Tempo de confirmação: _______________________

□ Transferência Bancária
   - Como identificam o cliente/fatura? _______________________
   - Manual ou automático? _______________________

□ Outras (especifique):
   _________________________________________________________________
```

---

## SEÇÃO 2: COMO VOCÊS ACESSAM OS DADOS HOJE

### 2.1 Extração de dados das plataformas

**2.1.1 Processo atual:**
```
O que fazem?
□ Fazem login e baixam relatório manualmente (frequência: ____________)
□ Existem APIs disponíveis que poderiam usar? Sim ( ) Não ( )
□ Usam alguma ferramenta de integração? (Zapier, Make, etc): ____________

Quanto tempo leva? ___________________
Quem faz isso? ___________________
Tem horário fixo? ___________________
```

**2.1.2 Qual informação extraem de cada plataforma?**
```
Para cada plataforma, quais informações vocês precisam?
- ID da Transação / Comprovante
- ID do Cliente
- Nome do Cliente
- CPF/CNPJ
- Valor
- Data do Pagamento / Esperado
- Status (aprovado, pendente, rejeitado)
- Tentativas de pagamento
- Descrição (o que foi pago?)

Outras informações específicas? ___________________________
```

---

## SEÇÃO 3: DADOS DOS CLIENTES / FATURAS

### 3.1 Onde vocês armazenam os dados de clientes e faturas?

```
□ Banco de dados próprio (qual sistema?): ___________________
□ Sistema de ERP (qual?): ___________________
□ Planilhas do Excel: ___________________
□ Google Sheets: ___________________
□ Sistema específico de cobranças (qual?): ___________________
□ Múltiplos lugares: ___________________
```

### 3.2 Informações que vocês têm de cada cliente

```
Para cada cliente, que informações vocês têm disponível?

✓ Básico:
- ID do Cliente
- Nome
- CPF / CNPJ
- Email
- Telefone / WhatsApp
- Endereço

✓ Financeiro:
- Fatura ID / Número
- Data de Emissão
- Data de Vencimento
- Valor da Fatura
- Valor Pago
- Saldo Devedor
- Data do Último Pagamento
- Histórico de pagamentos

✓ Status de Cobrança:
- Status atual (em dia, vencido, negativado)
- Quantos dias em atraso
- Data da última tentativa de cobrança
- Qual foi a última ação de cobrança
- Se foi negativado, quando
- Se foi desativado, quando

Que outras informações vocês têm? ___________________________
```

---

## SEÇÃO 4: PROCESSO ATUAL DE AVISOS E COBRANÇA

### 4.1 Como é feito HOJE (processo manual)?

**4.1.1 Identificação de inadimplentes:**
```
Como vocês descobrem que alguém está inadimplente?
□ Alguém consulta o sistema/planilha manualmente
□ Recebem uma notificação automática
□ Veem um relatório
□ Outra forma: _____________________________

Com que frequência fazem isso? _____________________________
Quanto tempo leva? _____________________________
```

**4.1.2 Avisos e cobranças:**
```
Qual é a SEQUÊNCIA de avisos que vocês fazem?

DIA -5 (antes do vencimento):
   □ Enviam aviso? Sim ( ) Não ( )
   □ Por qual canal? (Email, SMS, WhatsApp, Telefone): _______________
   □ Quem envia? (Pessoa, sistema automático): _______________

DIA 0 (vencimento):
   □ Fazem algo? Sim ( ) Não ( )
   □ O quê? _______________

DIA +5 / +10 (após vencimento):
   □ Qual é o intervalo? _______________
   □ Quantas tentativas fazem? _______________
   □ Por quais canais? _______________

DIA +30 (para negativação):
   □ Fazem inclusão em negativação? Sim ( ) Não ( )
   □ Em qual órgão? (Serasa, SPC, outro): _______________
   □ Quem autoriza? _______________

OUTROS:
   □ Há recebimento de contato após negativação? Sim ( ) Não ( )
   □ Se sim, como funciona? _______________
```

**4.1.3 Documentação de cobrança:**
```
Vocês registram/documentam as cobranças?
□ Sim, em: (banco de dados, planilha, outro): _______________
□ Não
□ Parcialmente

Que informações são registradas?
- Data/hora do contato
- Canal utilizado
- Resposta do cliente
- Resultado
- Observações

Quem acessa esse registro? _______________
```

---

## SEÇÃO 5: CAPACIDADE OPERACIONAL

### 5.1 Quantos clientes vocês têm?
```
Total de clientes: _______________
Clientes ativos (últimos 30 dias): _______________
Inadimplentes normalmente: _______________%
```

### 5.2 Quantas faturas por mês?
```
Total de faturas/transações por mês: _______________
Valor médio por fatura: _______________
Maior ticket: _______________
```

### 5.3 Equipe de cobranças
```
Quantas pessoas? _______________
Quantas horas por dia gastam com cobranças? _______________
Qual é o custo mensal dessa equipe (aprox)? _______________
```

---

## SEÇÃO 6: PROBLEMAS E PERDAS ATUAIS

### 6.1 Identifiquem os principais problemas:

```
□ Clientes em atraso que não foram contactados (por esquecimento)
□ Múltiplos contatos sem organização (cliente recebe vários avisos ao mesmo tempo)
□ Falta de rastreamento (não sabem se foi enviado aviso ou não)
□ Inadimplentes que ficam 60+ dias sem ação
□ Retrabalho (precisam revisar dados múltiplas vezes)
□ Relatórios manuais (leva muito tempo consolidar)
□ Erros nos dados (informações inconsistentes entre sistemas)
□ Custos de telefone/SMS altos
□ Falta de integração entre plataformas e sistema de cobrança
□ Outro: _______________
```

### 6.2 Impacto financeiro:

```
Quantos clientes são perdidos por mês por inadimplência? _______________
Quanto vocês deixam de receber por mês? _______________
Qual seria o impacto se reduzissem a inadimplência em 10%? _______________
```

---

## SEÇÃO 7: RESTRIÇÕES E LIMITAÇÕES

### 7.1 Existem limitações que precisamos considerar?

```
Técnicas:
□ Não têm API disponível das plataformas
□ Sistema antigo que é difícil integrar
□ Falta de infraestrutura
□ Outro: _______________

Legais/Compliance:
□ Há restrições para enviar mensagens automáticas (LGPD, etc)
□ Restrições para negativar (precisa de autorização, comprovação, etc)
□ Regulação específica do setor: _______________

Operacionais:
□ Usuários não têm conhecimento técnico para usar novas ferramentas
□ Orçamento limitado para novas ferramentas
□ Outro: _______________
```

---

## SEÇÃO 8: DESEJO FINAL

### 8.1 Se vocês pudessem ter um processo ideal, como seria?

```
Como vocês gostariam que funcionasse?
□ Totalmente automático (zero intervenção manual, exceto exceções)
□ Semi-automático (sistema avisa, pessoa aprova/envia)
□ Híbrido (automático para a maioria, manual para casos especiais)

Qual seria o impacto ideal?
- Redução de tempo: de _____ para _____
- Redução de custo: de _____ para _____
- Redução de inadimplência: de _____% para _____% 
- Aumento de recuperação: _____
```

---

## PRÓXIMOS PASSOS

1. **Você preenche este formulário** com as informações que temos
2. **Compartilha comigo** os dados específicos (se possível, sem informações sensíveis)
3. **Criamos junto** um novo processo que:
   - Automatize 90% do trabalho manual
   - Reduza tempo e custo
   - Aumente a taxa de recuperação
   - Seja escalável para crescimento

---

**Data de preenchimento:** _______________  
**Próxima reunião:** _______________
