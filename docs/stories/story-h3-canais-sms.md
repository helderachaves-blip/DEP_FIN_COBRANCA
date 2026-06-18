# STORY-H-03 — Canais de Comunicação + SMS (scaffold)

**Epic:** Fase H — Integrações · Sprint H-3
**Status:** InReview
**Branch:** `homologacao`

---

## Contexto

Hoje E-mail (Fase G) e WhatsApp (H-1) aparecem como abas soltas em Configurações.
O Sprint H-3 reorganiza a UX agrupando os canais sob um submenu único **"Canais de
Comunicação"** e adiciona o **SMS** como terceiro canal. O envio de SMS depende de um
provider ainda **não decidido** (Twilio / Zenvia / Comtele etc.), então esta entrega é o
**scaffold de configuração** — provider-agnostic — sem a camada de envio real.

## Objetivo

1. Agrupar E-mail + WhatsApp + SMS sob um cabeçalho "Canais de Comunicação" na sidebar.
2. Persistir a configuração de SMS por empresa, com a chave de API guardada **fora do banco**
   (mesmo padrão da credencial do Drive), pronta para quando o provider for integrado.

## Acceptance Criteria

- **AC-1** — Sidebar: as três abas de canais (E-mail, WhatsApp, SMS) ficam sob um
  cabeçalho de grupo "Canais de Comunicação" dentro do submenu Configurações.
- **AC-2** — Nova aba **SMS** em Configurações com: provider (select), remetente/Sender ID,
  chave de API/token, Account SID (opcional), endpoint (opcional) e toggle "canal ativo".
- **AC-3** — A chave de API é gravada em `secrets/sms_{empresa}.key` (marcador `[file]` na
  coluna); **nunca** aparece no HTML nem no banco. Campo vazio preserva a chave atual.
- **AC-4** — Na nuvem, a chave pode vir da env var `SMS_{empresa}_API_KEY` (precede o arquivo).
- **AC-5** — Migration `011_add_config_sms` cross-dialect (SQLite + Postgres).
- **AC-6** — Rota `POST /sms/configurar` (salvar) e `POST /sms/testar` (AJAX → JSON) que
  valida presença de provider + chave **sem chamar API externa** (envio ainda não habilitado).

> **Validação:** 11 testes em `tests/test_sms.py`. Suíte SQLite local: **116 passed, 1 skipped**.
- **AC-7** — Aviso explícito na aba de que o envio ainda não está habilitado (provider TBD).

## Notas de implementação

- `config_sms` espelha `config_whatsapp`: colunas genéricas (provider, sender_id,
  account_sid, api_key, endpoint, ativo) + timestamps. Segredo via arquivo em `secrets/`
  (testável: o `secrets/` cai no tempdir do conftest, não no Credential Store real).
- `db.salvar_config_sms` / `db.get_config_sms` / `db.get_sms_api_key` / `db.tem_sms_api_key`.
- `get_config_sms` remove `api_key` e expõe só `tem_api_key` (padrão de segurança do Drive).
- Sidebar: classe `.nav-subheader` nova para o rótulo de grupo.

## File List

- `06_APP/migrations/011_add_config_sms.py` — nova
- `06_APP/database.py` — helpers SMS (config + segredo em arquivo)
- `06_APP/app.py` — contexto `config_sms` + rotas `/sms/configurar` e `/sms/testar`
- `06_APP/templates/configuracoes.html` — aba SMS + JS de Testar Configuração
- `06_APP/templates/layout.html` — grupo "Canais de Comunicação" + sublink SMS + CSS
- `06_APP/tests/test_sms.py` — nova
- `06_APP/tests/test_migrations.py`, `tests/test_whatsapp.py` — asserções da lista de migrations atualizadas (1–11)

## Fora de escopo (v.next)

- **Camada de envio de SMS real** (integração com o provider escolhido) — depende da
  decisão de provider. O scaffold deixa config + segredo prontos.
- Envio SMS individual + em lote + registro em `envios` (`canal='sms'`).
- Mover fisicamente o conteúdo das abas E-mail/WhatsApp para dentro de uma aba-mãe
  aninhada (mantidas como abas irmãs; o agrupamento é feito na sidebar para não quebrar
  os deep-links `#tab-email`/`#tab-whatsapp` nem os redirects pós-save existentes).
