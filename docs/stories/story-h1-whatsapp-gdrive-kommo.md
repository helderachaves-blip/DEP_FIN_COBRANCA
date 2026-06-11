# STORY-H-01 — Integração WhatsApp via Google Drive + Kommo

**Epic:** Fase H — Integrações  
**Status:** Ready  
**Prioridade:** P0 — Primeira entrega da Fase H  
**Criado em:** 11/06/2026  
**Fonte:** Brainstorm Helder + Claude — 11/06/2026  

---

## Contexto

O app já gera mensagens formatadas por aluno na tela de Envio de Mensagens. Hoje o envio
pelo WhatsApp é manual (a Luana copia mensagem por mensagem). A integração com o Kommo CRM
elimina esse trabalho: o app gera uma planilha estruturada, sobe no Google Drive, e o Kommo
lê essa planilha e dispara as mensagens automaticamente pelo WhatsApp conectado a ele.

O tipo de mensagem enviada pelo Kommo é determinado pela `tag_crm` — campo que já existe
nos templates do app.

---

## Fluxo de Dados

```
App (Flask)
  └── Gera planilha XLSX estruturada
        └── Sobe no Google Drive (pasta configurada)
              └── Kommo lê via Make ou integração nativa Google Sheets
                    └── Dispara WhatsApp pelo número conectado ao Kommo
                          └── Tipo de mensagem = tag_crm da linha
```

---

## Estrutura da Planilha (a validar com o Kommo)

| Coluna | Exemplo | Observação |
|--------|---------|------------|
| `telefone` | `5511987654321` | Formato internacional, sem máscara |
| `nome` | `João Silva` | Nome completo |
| `tag_crm` | `INADIMPLENTE_REGUA` | Mapeia para template no Kommo |
| `empresa` | `INEPROTEC` | Para rastreio |
| `categoria` | `Régua` | Novos / Régua / Acima 30 Dias |
| `vencimento` | `01/06/2026` | Data de vencimento da fatura |
| `valor` | `R$ 350,00` | Valor formatado |

**Tags definidas:**
- `INADIMPLENTE_NOVO` — 1 dia de atraso
- `INADIMPLENTE_REGUA` — 2 a 29 dias
- `INADIMPLENTE_30DIAS` — 30+ dias

---

## Itens de Implementação

### 1. Migration `008_add_config_whatsapp`

Nova tabela `config_whatsapp` por empresa:

```sql
CREATE TABLE config_whatsapp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa TEXT NOT NULL UNIQUE,
    -- Google Drive
    gdrive_auth_method TEXT,        -- 'service_account' | 'oauth'
    gdrive_credentials TEXT,        -- JSON da Service Account (criptografado) ou token OAuth
    gdrive_folder_id TEXT,          -- ID da pasta de destino no Drive
    gdrive_filename_template TEXT,  -- ex: 'cobrancas_{empresa}_{data}.xlsx'
    -- Kommo
    kommo_webhook_url TEXT,         -- URL do webhook ou endpoint Make
    kommo_pipeline_id TEXT,         -- ID do pipeline (opcional)
    -- Comportamento
    exportar_automatico INTEGER DEFAULT 0,  -- 0 = sob demanda, 1 = automático
    -- Controle
    criado_em TEXT,
    atualizado_em TEXT
);
```

### 2. Aba de Configuração WhatsApp (em `configuracoes.html`)

Nova aba "WhatsApp" na página de Configurações, com três blocos:

**Bloco Google Drive:**
- Método de autenticação: radio `Service Account (JSON)` ou `OAuth`
- Upload do JSON da Service Account (ou fluxo OAuth)
- Campo: ID da pasta de destino no Drive
- Campo: Template do nome do arquivo (default: `cobrancas_{empresa}_{ddmmyyyy}.xlsx`)
- Botão **Testar Conexão** — valida credenciais + acesso à pasta (AJAX, padrão SMTP)

**Bloco Kommo:**
- Campo: URL do webhook (Make) ou ID do pipeline
- Campo: Tag CRM padrão (sugestão baseada nos templates cadastrados)

**Bloco Comportamento:**
- Toggle: Gerar planilha ao gerar relatório? (default OFF — sob demanda)

### 3. Botão "Exportar para WhatsApp" em `envio_mensagens.html`

- Aparece somente se a configuração do Google Drive estiver salva
- Ao clicar: gera o XLSX com os inadimplentes filtrados visíveis + faz upload no Drive
- Feedback: toast/flash com link para o arquivo no Drive
- Registra na tabela `envios` com `canal='whatsapp_crm'` e `qtd` enviada

### 4. Lógica de geração e upload (`processing.py` ou novo `gdrive.py`)

- Gerar XLSX com as colunas mapeadas acima
- Upload via Google Drive API (`googleapiclient` + `google-auth`)
- Substituir arquivo existente de mesmo nome (não acumular versões antigas)
- Retornar URL pública ou link de visualização do arquivo

### 5. Novas dependências (`requirements.txt`)

```
google-api-python-client>=2.100.0
google-auth>=2.23.0
google-auth-httplib2>=0.1.1
```

---

## Critérios de Aceite

- [ ] Aba "WhatsApp" aparece em Configurações para ambas as empresas
- [ ] Testar Conexão com Google Drive retorna sucesso/erro claro
- [ ] Credenciais da Service Account não aparecem em nenhum HTML renderizado
- [ ] Botão "Exportar para WhatsApp" aparece em Envio de Mensagens apenas quando configurado
- [ ] Planilha gerada tem as colunas corretas e telefones no formato internacional
- [ ] Upload no Drive cria/substitui o arquivo na pasta configurada
- [ ] Envio registrado na tabela `envios` com `canal='whatsapp_crm'`
- [ ] Funciona para INEPROTEC e MATRÍCULA EAD independentemente

---

## Decisões e Pendências

| Item | Status | Observação |
|------|--------|------------|
| Formato exato das colunas da planilha | ⏳ Validar com Kommo/Make | Pode ser necessário ajuste após teste real |
| Método de auth Google Drive | ⏳ Decidir | Service Account é mais simples para uso interno; OAuth para SaaS |
| Credenciais no banco | ⏳ Definir criptografia | Seguir padrão keyring ou colunas criptografadas |
| Integração Make vs. nativa Kommo | ⏳ Validar | Make é mais flexível; nativa mais simples |

---

## Dev Notes

- Seguir padrão da `config_email`: salvar/ler por empresa, senha/token nunca no HTML
- `gdrive_credentials` é sensível — avaliar keyring ou criptografia AES antes de salvar no banco
- O campo `tag_crm` já existe nos templates — reutilizar diretamente na geração da planilha
- Novos testes em `tests/test_whatsapp.py`: geração do XLSX, colunas, formato de telefone

---

*Helder + Claude — Brainstorm Fase H — 11/06/2026*
