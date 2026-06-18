# Onboarding H-1 — App → Google Drive → Kommo → WhatsApp

> Passo a passo operacional para ligar o fluxo real do WhatsApp via CRM. Fecha a STORY-H-01
> (InReview → Done). Pré-requisito: contas Google Workspace (`@ineprotec.com.br`) e Kommo.
> O **código já está pronto** (Ondas 1–2); aqui é só a configuração externa + validação.
> Última atualização: 18/06/2026.

---

## Visão geral das etapas

```
[A] Google Cloud: criar Service Account (SA) + baixar JSON
[B] Google Drive: criar Shared Drive + dar acesso à SA + pegar o folder_id
[C] Render: montar o JSON como Secret File + setar a env var
[D] App: configurar a aba WhatsApp + Testar Conexão
[E] App: exportar uma planilha de teste para o Drive
[F] Kommo: ler a planilha (nativo Google Sheets ou Make) + disparar WhatsApp
[G] Validar ponta a ponta → QA gate → Done
```

Etapas A, B, F dependem de acesso às contas do Edilvo (Google/Kommo). C, D, E são no nosso lado.

---

## [A] Google Cloud — Service Account

1. Acessar https://console.cloud.google.com com a conta Workspace do Edilvo.
2. Criar (ou escolher) um **projeto** (ex.: `matine-cobranca`).
3. **APIs & Services → Library →** habilitar a **Google Drive API**.
4. **APIs & Services → Credentials → Create credentials → Service account**.
   - Nome: ex. `matine-drive-sa`. Não precisa conceder papéis no projeto.
5. Na SA criada → aba **Keys → Add key → Create new key → JSON** → baixar o arquivo.
   - Esse JSON é a credencial. **Nunca** vai para o git nem para o banco.
6. Anotar o **e-mail da SA** (algo como `matine-drive-sa@<projeto>.iam.gserviceaccount.com`) —
   usado no passo [B].

---

## [B] Google Drive — Shared Drive

> Por que Shared Drive (e não "Meu Drive"): num Shared Drive os arquivos pertencem à
> **organização**, não à SA → elimina o erro `storageQuotaExceeded` (SA não tem cota própria).

1. No Google Drive, criar um **Shared Drive** (Drives compartilhados → Novo). Ex.: `MATINE Cobranças`.
2. (Opcional) Criar uma pasta dentro dele, ex. `INEPROTEC` e `MATRICULA_EAD` (uma por empresa).
3. **Adicionar a SA como membro** do Shared Drive (ou da pasta) com papel **Gerenciador de conteúdo**
   (Content manager) — usar o e-mail da SA do passo [A.6].
4. Abrir a pasta de destino e copiar o **ID da pasta** da URL:
   `https://drive.google.com/drive/folders/`**`<ESTE_ID>`** → é o `gdrive_folder_id`.

---

## [C] Render — Secret File + env var

> O app lê a credencial de `GOOGLE_SA_{empresa}_JSON_PATH` (env) antes de procurar em
> `DATA_DIR/secrets/` (ver EPIC-02 Onda 5). Na nuvem usamos Secret File.

1. Render → serviço **`matine-cobranca`** → **Environment → Secret Files → Add Secret File**.
   - Filename: ex. `/etc/secrets/gdrive_ineprotec.json` → colar o conteúdo do JSON da SA.
   - Repetir para a 2ª empresa se for usar Drive nas duas (`gdrive_matricula_ead.json`).
2. **Environment → Environment Variables →** adicionar:
   - `GOOGLE_SA_INEPROTEC_JSON_PATH` = `/etc/secrets/gdrive_ineprotec.json`
   - (e o equivalente para MATRÍCULA EAD, se aplicável)
   - ⚠️ Conferir o nome exato da env conforme `get_gdrive_credentials_path` em `database.py`
     (padrão `GOOGLE_SA_{EMPRESA}_JSON_PATH`, empresa em maiúsculas).
3. Salvar → o Render redeploya. (Local/dev: o JSON vai em `C:\MATINE\secrets\gdrive_{empresa}.json`.)

---

## [D] App — aba WhatsApp + Testar Conexão

1. Logar no app, selecionar a **empresa** no toggle da topbar.
2. **Configurações → Canais de Comunicação → WhatsApp**.
   - **Bloco Google Drive:** (se não usar a env do Render) fazer upload do JSON da SA;
     informar o **ID da pasta** (`gdrive_folder_id` do passo [B.4]); ajustar o template do
     nome do arquivo se quiser.
   - **Bloco Kommo:** URL do webhook (Make) ou ID do pipeline (preencher no passo [F]).
3. Clicar em **Testar Conexão** → deve retornar sucesso (valida credencial + acesso à pasta).
   - Erro comum: SA sem acesso ao Shared Drive (refazer [B.3]); folder_id errado;
     Drive API não habilitada ([A.3]).

---

## [E] App — exportar planilha de teste

1. Ter uma consolidação ativa (ou subir uma base de teste e consolidar).
2. **Envio de Mensagens → "Exportar para WhatsApp"** (só aparece com o Drive configurado).
3. Conferir no Shared Drive que o arquivo `CRM_{empresa}_{data}.xlsx` foi criado/substituído.
4. Conferir que o app registrou os envios (`canal='whatsapp_crm'`) — visível no histórico.

---

## [F] Kommo — ler a planilha + disparar

> Detalhes de capacidade em `kommo-plataforma.md`. Dois caminhos:

**Opção 1 — nativo Google Sheets (mais simples):**
1. No Kommo: Settings → Integrations → **Google Sheets** → conectar a conta Google.
2. Apontar para a planilha (pode ser necessário o arquivo estar como **Google Sheets**, não
   XLSX — validar; se preciso, converter no Drive ou usar Make).
3. Mapear: **cada nova linha → novo lead**; mapear coluna `Tag CRM` → tag do lead.
4. Configurar **Salesbot/Broadcast** para disparar o WhatsApp conforme a tag.

**Opção 2 — Make (mais flexível):**
1. Cenário no Make: trigger no arquivo do Drive → criar/atualizar lead no Kommo + aplicar `tag_crm`.
2. Disparar Salesbot/automação a partir da tag.

---

## [G] Validação ponta a ponta → QA gate

- [ ] Testar Conexão verde no app (ambas as empresas, se aplicável)
- [ ] Planilha aparece no Shared Drive (criada/substituída, sem duplicar versões)
- [ ] Kommo cria/atualiza os leads a partir da planilha
- [ ] WhatsApp dispara a mensagem correta conforme a `tag_crm`
- [ ] Mensagem chega de fato no número de teste
- [ ] Envios registrados no app (`canal='whatsapp_crm'`)

Com todos os itens OK → STORY-H-01 passa de **InReview → Done** (QA gate).

---

## Troubleshooting rápido

| Sintoma | Causa provável | Ação |
|---------|----------------|------|
| `storageQuotaExceeded` | Usou "Meu Drive" em vez de Shared Drive | Refazer [B] com Shared Drive |
| Testar Conexão falha (403/404 na pasta) | SA sem acesso ou folder_id errado | [B.3] / [B.4] |
| `Drive API has not been used` | API não habilitada | [A.3] |
| App não mostra "Exportar para WhatsApp" | Drive não configurado p/ a empresa ativa | [D] |
| Kommo não lê o XLSX | Integração nativa espera Google Sheets | Converter ou usar Make [F] |

---

## Referências

- STORY-H-01: `docs/stories/story-h1-whatsapp-gdrive-kommo.md`
- Guia da plataforma: `docs/guides/kommo-plataforma.md`
- Código: `06_APP/gdrive.py`, rotas `/whatsapp/*` em `06_APP/app.py`,
  helpers `get_gdrive_credentials_path` em `06_APP/database.py`
