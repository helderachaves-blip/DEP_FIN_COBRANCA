# 06_APP — Cobranças INE-MAT (aplicação web)

Consolidador de inadimplências multi-empresa (Ineprotec / Matrícula EaD).
Backend Flask + SQLite, frontend Bootstrap. Roda localmente em `http://localhost:5000`.

## 🚀 Onboarding (máquina nova)

1. Instale o **Python 3.10+** (no Windows, marque "Add Python to PATH").
2. Na pasta `06_APP`, instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Suba o app:
   ```
   python app.py
   ```
4. Acesse `http://localhost:5000`.

A estrutura de dados em `C:\MATINE\` é **criada automaticamente** no primeiro boot
(`setup_inicial()` em `app.py`) — pastas, banco SQLite versionado e templates padrão
por empresa. Banco vazio é aceitável para desenvolvimento.

> Para levar os dados de produção para outra máquina, copie a pasta `C:\MATINE\` inteira.
> Os dados ficam **fora** do projeto (não versionados).

## 🔐 Login

O acesso é protegido (Flask-Login). Credenciais padrão de fábrica, semeadas no `.env`
na primeira execução:

| Usuário | Senha |
|---------|-------|
| `luana` | `matine2026` |

**Troque a senha antes de produção.** Edite `06_APP/.env` (gitignored) — gere um hash com:
```
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('suasenha', method='pbkdf2:sha256'))"
```
e cole em `APP_SENHA`. Modelo completo em `.env.example`.

## 📊 Fluxo de uso

1. **Importar** arquivos (Vencidos + Alunos, opcional A Vencer / Pagos-Cancelados).
2. **Consolidar** → revisar em **Resultado**.
3. **Gerar Relatórios** (TXT/XLSX por régua).
4. **Envio de Mensagens** (WhatsApp manual + e-mail SMTP).
5. **Atualizar Base** para persistir e detectar quitados/renegociados.

## 🗂️ Estrutura `C:\MATINE\`

```
C:\MATINE\
├── banco\inadimplencia.db   # SQLite (schema versionado via migrations\)
├── uploads\{EMPRESA}\{tipo}\
├── relatorios\{EMPRESA}\{ano}\{mes}\{dia}\
├── crm-exports\
├── estado\                  # sessão (pickle)
└── logs\
```

## 🧩 Dependências

`flask`, `flask-login`, `pandas`, `openpyxl`, `keyring` (ver `requirements.txt`).
Se faltar alguma, o app exibe instrução amigável no startup em vez de stack trace.

## 💾 Backup do banco

Script de backup com retenção (cópia consistente via API do sqlite3, funciona com WAL):

```
python backup_db.py            # mantém os 14 backups mais recentes
python backup_db.py --keep 30  # mantém 30
```

Os backups vão para `C:\MATINE\backups\`. Pode ser agendado no **Agendador de Tarefas do
Windows** para rodar diariamente.

## 🧪 Testes

Suíte automatizada com **pytest** (rede de regressão para auth, migrations,
multiusuário e processamento). Os testes rodam **isolados**: usam um banco temporário
via `MATINE_DATA_DIR` e **nunca tocam** os dados de produção em `C:\MATINE`.

```
pip install -r requirements-dev.txt
pytest
```

Cobertura por arquivo (`tests/`): `test_processing` (CSV/valores/gênero/consolidação),
`test_migrations` (runner + up/down da 007), `test_auth` (login/guard/logout/open-redirect),
`test_usuarios` (CRUD + anti-lockout), `test_conta` (nome + senha).

---
*Parte do EPIC-01 (Sprint Zero). Gestão do projeto: `MEMORY.md` / `PLANO_DE_ACAO.md` / `ROADMAP.md` na raiz.*
