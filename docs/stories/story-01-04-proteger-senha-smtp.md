# STORY-01-04: Proteger Senha SMTP com Python Keyring
**Epic:** EPIC-01 Sprint Zero
**Status:** Done
**Esforco estimado:** ~4h
**Prioridade:** P1
**Debitos resolvidos:** DB-C01, SEC-02

---

## Contexto

A senha SMTP esta armazenada em texto plano na coluna `smtp_senha` da tabela `config_email`. Qualquer copia do arquivo `inadimplencia.db` (backup, transferencia, acesso indevido) expos a senha do e-mail corporativo. A solucao e armazenar a senha no Windows Credential Store via biblioteca `keyring`.

---

## Acceptance Criteria

### AC-01 — Instalacao de dependencia
- [x] `keyring` adicionado ao `06_APP/requirements.txt` (`keyring>=25.0.0`)
- [x] `pip install keyring` funcional (keyring 25.7.0, backend **WinVaultKeyring** = Windows Credential Manager)

### AC-02 — Salvar senha no Windows Credential Store
- [x] `salvar_config_email` armazena via `keyring.set_password("matine-smtp", empresa, senha)` em vez de gravar a senha na coluna
- [x] Coluna `smtp_senha` recebe o marcador `"[keyring]"` (nunca a senha real)
- [x] Migracao de seguranca (`migrar_senhas_smtp`): senha em texto plano e movida para o keyring e a coluna vira marcador, no startup (`init_db`). **Verificado no banco real:** senha INEPROTEC migrada, coluna agora `[keyring]`

### AC-03 — Ler senha do Windows Credential Store
- [x] `get_config_email(empresa)` popula `smtp_senha` via `_ler_senha_smtp` (keyring → env → coluna-legado)
- [x] Se nenhuma fonte tiver a senha, retorna `None` (nao string vazia)

### AC-04 — Formulario de configuracao SMTP
- [x] Campo de senha e `type="password"`
- [x] Exibe placeholder `••••••••` quando configurada; o valor real NUNCA vai para o HTML (rota remove a senha antes de renderizar; flag `smtp_senha_set`)
- [x] Enviar com o campo vazio NAO sobrescreve a senha atual (`salvar_config_email` só toca no keyring se `senha` vier preenchida) — testado

### AC-05 — Teste SMTP funcional apos migracao
- [x] `/email/testar`, `/email/enviar-aluno`, `/email/enviar-todos` inalterados: consomem `config['smtp_senha']`, que agora vem do keyring. Caminho de login SMTP idêntico ao anterior; resolução da senha via keyring verificada (login real no Gmail não testado — credencial de teste fictícia)

---

## Arquivos a Modificar

- `06_APP/database.py` — funcoes `salvar_config_email` e `get_config_email`
- `06_APP/app.py` — rota `/email/configurar` (chamada para database)
- `06_APP/requirements.txt` — adicionar `keyring`

---

## Testes Esperados

- [x] Configurar SMTP com senha real: coluna fica com marcador `[keyring]`, senha NAO aparece em texto no banco (verificado)
- [x] Senha persistida no Windows Credential Store (round-trip keyring OK)
- [x] Campo de senha no formulario: placeholder de bullets quando configurado; senha real ausente do HTML (verificado via curl)
- [x] Salvar sem alterar a senha (campo vazio): senha existente nao e apagada (testado)
- [x] Migracao de senha legada em texto plano → keyring (idempotente; testado + banco real)
- [x] Fallback de variavel de ambiente `SMTP_<EMPRESA>_SENHA` (testado)
- [ ] Login real no Gmail com a senha do keyring — não exercitado nesta sessão (sem credencial válida de teste); caminho de código inalterado

---

## Nota de Rollback

Se o keyring falhar (ex.: ambiente sem credential store), o sistema loga
`"Keyring não disponível. Configure SMTP_<EMPRESA>_SENHA como variável de ambiente."`
e usa o fallback `SMTP_INEPROTEC_SENHA` / `SMTP_MATRICULAEAD_SENHA`. Implementado em
`_ler_senha_smtp` / `_gravar_senha_smtp`. A migração mantém a senha na coluna se o keyring
falhar (não quebra envios), com aviso no log.

---

## File List

- `06_APP/requirements.txt` — adiciona `keyring>=25.0.0`
- `06_APP/database.py` — import protegido de keyring; `_env_senha`, `_gravar_senha_smtp`,
  `_ler_senha_smtp`, `migrar_senhas_smtp`; `salvar_config_email`/`get_config_email`
  reescritas; chamada de migração no `init_db()`
- `06_APP/app.py` — rota `/configuracoes` passa `smtp_senha_set` e remove a senha do contexto
- `06_APP/templates/configuracoes.html` — campo senha sem `value`, placeholder de bullets + helptext condicional

## Dev Notes

- **Interface preservada:** todo o código de envio/teste SMTP (`_enviar_email_smtp`,
  `/email/testar`, `/email/enviar-*`) continua lendo `config['smtp_senha']` — só a origem
  mudou (keyring em vez da coluna). Zero alteração no caminho de login.
- **Ordem de leitura da senha:** keyring → variável de ambiente → coluna (legado). O fallback
  de coluna evita regressão se a migração ainda não rodou ou o keyring estiver indisponível;
  após a migração a coluna tem só o marcador, então o fallback retorna None e o keyring manda.
- **Não vaza no HTML:** a rota tira a senha do `config_email` antes de renderizar e passa
  apenas `smtp_senha_set`. O input usa `value=""` + placeholder de bullets.
- **Migração roda em conexão própria** após o fechamento da conexão das migrations (evita
  duas conexões simultâneas ao mesmo arquivo).
- **Validação:** suite temporária (marcador na coluna, leitura do keyring, vazio preserva,
  migração legada, idempotência, fallback env) 100% PASS; banco real migrado (senha plana
  movida ao keyring, coluna = `[keyring]`); rotas 200; senha ausente do HTML.

## Change Log

| Data | Status | Autor | Nota |
|------|--------|-------|------|
| (origem) | Draft | @sm | Story criada |
| 10/06/2026 | Draft -> Done | @dev | Senha SMTP movida para keyring (Windows Credential Store) com fallback env/coluna; migração de senha legada no startup; UI sem vazamento. Testado e banco real migrado |

---

*STORY-01-04 — EPIC-01 Sprint Zero — MAT-INE Inadimplencia 2026*
