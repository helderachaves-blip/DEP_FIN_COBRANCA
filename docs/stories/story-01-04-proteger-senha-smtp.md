# STORY-01-04: Proteger Senha SMTP com Python Keyring
**Epic:** EPIC-01 Sprint Zero
**Status:** Draft
**Esforco estimado:** ~4h
**Prioridade:** P1
**Debitos resolvidos:** DB-C01, SEC-02

---

## Contexto

A senha SMTP esta armazenada em texto plano na coluna `smtp_senha` da tabela `config_email`. Qualquer copia do arquivo `inadimplencia.db` (backup, transferencia, acesso indevido) expos a senha do e-mail corporativo. A solucao e armazenar a senha no Windows Credential Store via biblioteca `keyring`.

---

## Acceptance Criteria

### AC-01 — Instalacao de dependencia
- [ ] `keyring` adicionado ao `06_APP/requirements.txt`
- [ ] `pip install keyring` funcional no Python 3.14 do ambiente da Luana

### AC-02 — Salvar senha no Windows Credential Store
- [ ] Rota `/email/configurar`: ao salvar configuracao SMTP, senha e armazenada via `keyring.set_password("matine-smtp", empresa, senha)` em vez de INSERT na coluna `smtp_senha`
- [ ] Coluna `smtp_senha` na tabela `config_email` recebe valor vazio ou marcador `"[keyring]"` em vez da senha real
- [ ] Migracao de seguranca: registro existente com senha em texto plano e sobrescrito por `"[keyring]"` e a senha e movida para o keyring na primeira execucao apos o deploy

### AC-03 — Ler senha do Windows Credential Store
- [ ] Funcao `get_config_email(empresa)` em `database.py` retorna a senha via `keyring.get_password("matine-smtp", empresa)` em vez de ler a coluna `smtp_senha`
- [ ] Se `keyring.get_password` retornar `None` (senha nao configurada), o campo senha e retornado como `None` — nao como string vazia

### AC-04 — Formulario de configuracao SMTP
- [ ] Campo de senha no formulario de configuracoes e `type="password"` (ja e? verificar)
- [ ] Ao abrir a aba de configuracoes, o campo de senha exibe `••••••••` (8 pontos) se senha esta configurada no keyring, ou vazio se nao esta
- [ ] Enviar o formulario com o campo de senha vazio NAO sobrescreve a senha atual no keyring (comportamento: preservar senha existente se campo vier vazio)

### AC-05 — Teste SMTP funcional apos migracao
- [ ] Rota `/email/testar` funciona normalmente apos a mudanca (busca senha do keyring)
- [ ] Envio de e-mail individual (`/email/enviar-aluno`) funciona normalmente
- [ ] Envio em lote (`/email/enviar-todos`) funciona normalmente

---

## Arquivos a Modificar

- `06_APP/database.py` — funcoes `salvar_config_email` e `get_config_email`
- `06_APP/app.py` — rota `/email/configurar` (chamada para database)
- `06_APP/requirements.txt` — adicionar `keyring`

---

## Testes Esperados

- [ ] Configurar SMTP com senha real: senha NAO aparece em texto em `inadimplencia.db` (verificar com DB Browser for SQLite)
- [ ] Testar conexao: autentica no Gmail com senha do keyring
- [ ] Reiniciar o servidor: senha ainda funciona (persistida no Windows Credential Store)
- [ ] Campo de senha no formulario: mostra bullets se configurado, vazio se nao configurado
- [ ] Salvar sem alterar a senha (campo vazio): senha existente nao e apagada

---

## Nota de Rollback

Se o keyring falhar em algum ambiente (ex: servidor sem interface grafica), o sistema deve logar um erro claro:
`"Keyring nao disponivel. Configure SMTP_[EMPRESA]_SENHA como variavel de ambiente."` e buscar fallback em variavel de ambiente `SMTP_INEPROTEC_SENHA` / `SMTP_MATRICULAEAD_SENHA`.

---

*STORY-01-04 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
