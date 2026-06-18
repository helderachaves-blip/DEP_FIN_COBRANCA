# Guia da Plataforma Kommo — para o MAT-INE Inadimplência

> Documento de referência (não é arquivo de gestão). Objetivo: entender o que o Kommo faz,
> o que ele consegue (e o que **não** consegue) disparar, e como o nosso app se encaixa.
> Última atualização: 18/06/2026. Fonte: pesquisa web + decisões do projeto.

---

## 1. O que é o Kommo

Kommo (ex-**amoCRM**) é um **CRM "messenger-first"**: foi desenhado em torno de
conversas. O centro do produto é um **inbox unificado** + **pipeline de vendas/atendimento**,
com automação por **Salesbot** (bot sem código) e **broadcasts** (envios em massa).

Para o nosso caso (cobrança de inadimplentes), ele atua como o **executor de disparos**:
o app classifica e gera os dados, o Kommo envia as mensagens e registra tudo no "lead".

---

## 2. O que o Kommo consegue disparar

| Canal | Suporte no Kommo | Como funciona |
|-------|------------------|---------------|
| **WhatsApp** | ✅ **Nativo** (é o forte dele) | Número conectado ao Kommo; envia por conversa, Salesbot ou broadcast |
| **E-mail** | ✅ **Nativo** | Canal no inbox unificado |
| **Instagram / Telegram / Messenger / Viber** | ✅ **Nativo** | Caso o produto cresça para esses canais |
| **SMS** | ⚠️ **NÃO nativo** | Só via **gateway terceiro**: **Twilio**, **RingCentral** ou **Fromni** |

### ⚠️ O ponto crítico sobre SMS

O Kommo **não vende SMS** nem envia SMS sozinho. Ele apenas "pluga" um provedor:
- **Twilio** é a integração SMS plug-and-play (Settings → Integrations → Twilio Text Messaging →
  informar Account SID + Auth Token + número).
- Provedores **brasileiros** (Comtele, Zenvia) **não** aparecem na lista nativa de SMS do Kommo.
  Para usá-los, seria via **Make/Salesbot + webhook HTTP** (mais trabalho).

**Consequência:** não existe SMS "de graça" em lugar nenhum — nem direto do app, nem pelo
Kommo. Habilitar SMS **sempre** exige contratar um gateway. Por isso, no nosso roadmap, o SMS
fica como **scaffold pronto, sem contratação** (ver `PLANO_DE_ACAO.md` / `ROADMAP.md`).

---

## 3. Automação: Salesbot e Broadcast

- **Salesbot** — bot visual (sem código) que dispara mensagens em estágios do pipeline,
  responde FAQs, aplica tags, move o lead, etc. Reage a **palavras-chave** e a eventos.
  Disponível a partir do plano **Avançado**.
- **Broadcast** — envio de uma mensagem para um público-alvo, por um ou vários canais
  (ex.: WhatsApp Business + Instagram). Útil para campanhas/lembretes em lote.

No nosso fluxo, o disparo de cobrança é dirigido pela **`tag_crm`** de cada linha: a tag
seleciona qual template/mensagem o Salesbot ou broadcast envia.

---

## 4. Como o Kommo lê a planilha do app

O app já gera a **Planilha CRM** (`proc.gerar_planilha_crm`, aba `Inadimplentes`) e sobe no
**Google Drive** (STORY-H-01). Do Drive ao Kommo há dois caminhos:

| Caminho | Como | Quando usar |
|---------|------|-------------|
| **Integração nativa Google Sheets** | "Cada nova linha na planilha vira um lead no pipeline." Na importação, o Kommo anexa uma **tag de import** automática (filtrável). | Mais simples; bom para começar |
| **Make (ex-Integromat)** | Cenário lê a planilha/arquivo e cria/atualiza leads + aplica `tag_crm`, dispara Salesbot. | Mais flexível (transformações, dedupe, regras) |

> Detalhe importante: a integração nativa lê **Google Sheets** (planilha nativa), não XLSX
> solto. Se formos pela via nativa, pode ser necessário o arquivo estar como **Google Sheets**
> (ou um passo de conversão no Make). Validar no onboarding (ver `onboarding-h1-whatsapp-drive-kommo.md`).

### Colunas que o Kommo precisa (essenciais)

Da aba `Inadimplentes`: **`Telefone`** (formato internacional, ex. `5511987654321`) +
**`Tag CRM`** são o mínimo para o disparo. As demais (Nome, Categoria, Valor, Vencimento)
enriquecem o lead e permitem segmentar.

### Tags de cobrança

| Tag | Critério |
|-----|----------|
| `INADIMPLENTE_NOVO` | 1 dia de atraso |
| `INADIMPLENTE_REGUA` | 2 a 29 dias |
| `INADIMPLENTE_30DIAS` | 30+ dias |

Cada tag mapeia para um template/mensagem configurado no Kommo.

---

## 5. Planos e custos (para avaliação)

| Plano | Preço (por usuário/mês) | Destaque |
|-------|-------------------------|----------|
| **Base** | US$ 15 | CRM essencial |
| **Avançado** | US$ 25 | **Salesbot** + automação + IA |
| **Enterprise** | US$ 45 | Suíte completa |

- A automação que interessa (Salesbot) começa no **Avançado**.
- **SMS é custo à parte:** mesmo via Kommo, paga-se por mensagem ao gateway (ex.: Twilio
  ~US$ 0,06/SMS). O Kommo centraliza, mas não elimina o custo do provedor.

---

## 6. Arquitetura resultante (app ↔ Kommo)

```
App (Flask)  =  cérebro de dados
  · classifica inadimplentes (Novos / Régua / 30+)
  · define tag_crm por linha
  · gera Planilha CRM → sobe no Google Drive
        │
        ▼
Kommo  =  executor de disparos
  · lê a planilha (nativo Google Sheets ou Make)
  · cria/atualiza leads, aplica tag_crm
  · Salesbot/Broadcast dispara WhatsApp (e, se contratado, SMS via gateway)
  · registra tudo no lead (histórico por contato)
```

**Implicação de produto:** com o Kommo como hub, o app **não precisa** enviar WhatsApp nem SMS
diretamente — basta alimentar dados + tags. Por isso **não** vale construir o envio SMS
app-side (Comtele/Zenvia) enquanto a estratégia for Kommo-first; o scaffold atual já
"deixa pronto" sem contratação.

---

## 7. Decisões em aberto (validar no onboarding)

- **Nativo Google Sheets vs Make:** começar pelo mais simples (nativo) e migrar para Make se
  precisar de regras (dedupe, transformação, múltiplas tags).
- **Formato do arquivo:** XLSX no Drive precisa virar Google Sheets para a via nativa? Testar.
- **SMS:** se um dia habilitar, decidir entre **Twilio dentro do Kommo** (zero código no app,
  vira só mais um canal dirigido pela `tag_crm`) **ou** envio direto do app via **Comtele**
  (mais barato no BR, mas duplica caminho de disparo). Recomendação atual: se Kommo-first,
  Twilio-no-Kommo é mais coerente.

---

## Fontes

- Kommo — site e suporte: https://www.kommo.com/ · https://www.kommo.com/support/crm/broadcasting/
- Kommo — Messaging & SMS (gateways): https://www.kommo.com/integrations/messaging-sms/
- Kommo — Twilio Text Messaging: https://www.kommo.com/integrations/twilio-sms/ · https://www.kommo.com/support/integrations/twilio-text-messaging/
- Kommo — Google Sheets: https://www.kommo.com/support/integrations/google-sheets/ · https://www.kommo.com/integrations/google-sheets-integration/
- Kommo — Importar dados: https://www.kommo.com/support/crm/how-to-import/
