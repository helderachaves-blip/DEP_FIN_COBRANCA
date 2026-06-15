# STORY-H-01 — Integração WhatsApp via Google Drive + Kommo

**Epic:** Fase H — Integrações  
**Status:** InProgress  
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
| Formato exato das colunas da planilha | ✅ Decidido (15/06) | Reaproveitar a Planilha CRM existente (`proc.gerar_planilha_crm`), aba `Inadimplentes`. Ajuste fino possível após teste real com o Kommo |
| Método de auth Google Drive | ✅ Decidido (15/06) | Service Account + Shared Drive (Workspace `@ineprotec.com.br`). `gdrive.py` modular para OAuth na v2 |
| Credenciais no banco | ✅ Decidido (15/06) | JSON da SA em `C:\MATINE\secrets\gdrive_{empresa}.json`; coluna `gdrive_credentials` guarda só o marcador `[file]` (JSON excede o limite do keyring) |
| Integração Make vs. nativa Kommo | ⏳ Validar | Make é mais flexível; nativa mais simples |

---

## Dev Notes

- Seguir padrão da `config_email`: salvar/ler por empresa, senha/token nunca no HTML ✅ (espelhado)
- `gdrive_credentials` é sensível — resolvido: JSON em `secrets/`, coluna com marcador `[file]`
- O campo `tag_crm` já existe nos templates — reutilizar diretamente na geração da planilha
- Novos testes em `tests/test_whatsapp.py`: migration 008, config round-trip, gdrive (create/replace)

---

## Progresso de Implementação

### ✅ Onda 1 — Fundação backend (15/06/2026)

CLI-First: a camada de dados + upload funciona e é testada antes da UI.

- [x] **Migration `008_add_config_whatsapp`** — tabela `config_whatsapp` por empresa (up/down)
- [x] **`database.py`** — `salvar_config_whatsapp` / `get_config_whatsapp` + helpers de credencial
      (`gravar_gdrive_credentials`, `get_gdrive_credentials_path`, `tem_gdrive_credentials`).
      Credencial fora do banco (arquivo em `secrets/`); `get_config_whatsapp` nunca expõe o JSON.
- [x] **`gdrive.py`** — módulo modular (SA + Shared Drive, `supportsAllDrives=True`):
      `disponivel()`, `testar_conexao()`, `upload_xlsx()` (cria/substitui). Imports do Google
      protegidos → app não quebra sem as libs. Camada de auth isolada p/ OAuth na v2.
- [x] **`requirements.txt`** — `google-api-python-client`, `google-auth`, `google-auth-httplib2`
- [x] **`tests/test_whatsapp.py`** — 12 testes (migration, config, gdrive). Suíte total: **64 verdes**

### 🔲 Onda 2 — UI + fluxo (próxima sessão / nova janela)

- [ ] Aba "WhatsApp" em `configuracoes.html` (blocos Drive + Kommo + Comportamento) + rotas
- [ ] Botão **Testar Conexão** (AJAX, padrão SMTP) chamando `gdrive.testar_conexao`
- [ ] Botão **"Exportar para WhatsApp"** em `envio_mensagens.html` → gera Planilha CRM + `gdrive.upload_xlsx`
- [ ] Registro em `envios` com `canal='whatsapp_crm'`
- [ ] Garantir que a credencial nunca apareça em HTML renderizado (AC)

## File List

- `06_APP/migrations/008_add_config_whatsapp.py` (novo)
- `06_APP/gdrive.py` (novo)
- `06_APP/tests/test_whatsapp.py` (novo)
- `06_APP/database.py` (config_whatsapp + helpers de credencial)
- `06_APP/requirements.txt` (libs Google)
- `06_APP/tests/test_migrations.py` (expectativa migration 8)

## Change Log

| Data | Autor | Mudança |
|------|-------|---------|
| 11/06/2026 | @sm | Story criada (Draft) a partir do brainstorm da Fase H |
| 15/06/2026 | Helder | Bloqueadores resolvidos: formato (Planilha CRM) + auth (Service Account + Shared Drive) |
| 15/06/2026 | @dev | Ready → InProgress; Onda 1 (fundação backend) implementada e testada (64 testes verdes) |

---

*Helder + Claude — Brainstorm Fase H — 11/06/2026*
