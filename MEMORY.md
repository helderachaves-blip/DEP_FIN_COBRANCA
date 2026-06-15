# MEMORY — MAT-INE Inadimplência 2026

> Contexto permanente do projeto. Atualizar apenas quando algo estrutural mudar.
> Última atualização: 15/06/2026

---

## Pessoas

| Papel | Nome | Contato |
|-------|------|---------|
| Gestor / dono do projeto | Edilvo | gerente@ineprotec.com.br |
| Operadora diária | Luana | Não técnica — usa o app via browser |
| TI / Arquitetura | Helder | helderachaves@gmail.com |

---

## Empresas

| Empresa | Sistema | Observação |
|---------|---------|------------|
| **INEPROTEC** | Synapta | Escola Técnica |
| **MATRÍCULA EAD** | Synapta (portal.matriculaead.com.br) | Consultoria Educacional |

O app é multi-empresa. A empresa ativa é selecionada pelo toggle na topbar. Cada empresa tem banco, uploads, relatórios e templates separados.

---

## Objetivo

Automatizar cobrança de faturas vencidas.
**Meta:** reduzir de 2,5–4h/dia → ~15 min/dia.
**Canais:** WhatsApp (manual via wizard, futuro automático) + E-mail SMTP.

---

## Stack Técnica

| Componente | Tecnologia |
|-----------|-----------|
| Backend | Python / Flask |
| Banco | SQLite (`C:\MATINE\banco\inadimplencia.db`) |
| Frontend | Bootstrap 5.3.3 + Jinja2 |
| Processamento | pandas |
| Branch de trabalho | `homologacao` |

---

## Como Rodar

```powershell
# Subir
cd "F:\DADOS\CONSULTORIA\EDILVO SOUSA\AUTOMACOES IA\dep-financeiro\mat-ine - inadimplencia - 2026\06_APP"
python app.py
# Acessar: http://localhost:5000

# Parar
Get-Process python* | Stop-Process -Force
```

**Onboarding em máquina nova (ex.: colaborador de dev):**
1. Instalar Python 3.10+ ("Add to PATH")
2. `cd` na pasta `06_APP` → `pip install -r requirements.txt`
3. `python app.py` → a estrutura `C:\MATINE` é criada automaticamente no startup
4. O `.env` (gitignored) é gerado na 1ª execução com a `FLASK_SECRET_KEY` (`app.py:_carregar_secret_key`)
> Dados ficam em `C:\MATINE` (fora do projeto). Banco vazio é OK para dev; para levar dados, copiar `C:\MATINE\` inteira. Tornar isso robusto = STORY-01-07 (backlog).

---

## Estrutura de Dados

```
C:\MATINE\
├── banco\inadimplencia.db       # banco SQLite principal
├── uploads\{EMPRESA}\{tipo}\    # arquivos importados (detecção por pasta)
├── relatorios\{EMPRESA}\{ano}\{mes}\{dia}\   # relatórios gerados
├── crm-exports\                 # planilhas de tagging CRM
├── secrets\                     # JSON da Service Account do Drive (gdrive_{empresa}.json) — STORY-H-01
├── estado\                      # sessão pickle (consolidado, avencer, stats)
└── logs\
```

---

## Arquivos Fonte (exportados do Synapta)

| Arquivo | Formato | Descrição |
|---------|---------|-----------|
| `(NNN) Faturas.csv` | CSV `,` sem cabeçalho, utf-8 | Faturas vencidas |
| `(298) Alunos.csv` | CSV `,` | Cadastro de alunos (~5.200 registros) |
| `NAO PAGOS - VINCENDAS - DD-MM-AAAA.csv` | CSV | Faturas a vencer |

**Atenção:** Synapta pode exportar com separador `;` ou `,` e com/sem linha de cabeçalho extra. O processamento testa automaticamente múltiplas combinações.

---

## Classificação de Inadimplentes

| Categoria | Critério | Frequência de contato |
|-----------|----------|----------------------|
| Novos Inadimplentes | 1 dia de atraso | Diária |
| Régua (2–29 dias) | 2 a 29 dias de atraso | Diária |
| Acima 30 Dias | 30+ dias de atraso | 1x por semana |

---

## Templates de Mensagem

**Mensagem A — Novos e Régua**
```
Olá, {sr./sra.} {NOME}. Tudo bem?
Somos do setor financeiro do Matricula EaD.
Para sua maior comodidade estamos enviando o boleto referente ao seu Curso
Técnico, com vencimento em {DATA_VENCIMENTO}.
Se já realizou o pagamento, favor desconsiderar a mensagem!
Qualquer dúvida estamos à disposição!
```

**Mensagem B — Acima 30 Dias**
```
Olá, {sr./sra.} {NOME}. Tudo bem?
Somos do setor financeiro do Matricula EaD. O motivo do meu contato é
referente às parcelas em aberto do seu Curso Técnico.
Tem interesse em retornar ao curso?
```

Templates são configuráveis em Configurações → Mensagens. Cada template tem campo `tag_crm` para integração com Kommo.

---

## Tabelas do Banco

| Tabela | Descrição |
|--------|-----------|
| `inadimplentes` | Base persistente (PK composta: cpf + empresa) |
| `templates` | Mensagens configuráveis por empresa (com tag_crm) |
| `envios` | Histórico de envios por canal/dia/empresa |
| `config_email` | Config SMTP por empresa. **Senha NÃO fica aqui** — vai para o keyring (Windows Credential Store); a coluna `smtp_senha` guarda só o marcador `[keyring]` (STORY-01-04) |
| `historico_atualizacoes` | Log de atualizações da base |
| `schema_migrations` | Controle de versão do schema (version, name, applied_at) — STORY-01-05 |
| `usuarios` | Login por pessoa (usuario único, nome, senha_hash pbkdf2, is_admin, ativo) — STORY-MULTIUSUARIO (migration 007) |
| `config_whatsapp` | Config WhatsApp/Drive por empresa (migration 008, STORY-H-01). **Credencial da SA NÃO fica aqui** — JSON vai para `C:\MATINE\secrets\gdrive_{empresa}.json`; a coluna `gdrive_credentials` guarda só o marcador `[file]` |

**Autenticação (STORY-01-06 → STORY-MULTIUSUARIO):** multi-usuário via tabela `usuarios`. Login/`user_loader` consultam o banco; senha sempre hash pbkdf2. O `.env` (`APP_USUARIO`/`APP_SENHA`) serve **só como semente** do 1º admin na tabela vazia — depois disso a gestão é pela tela `/usuarios` (admin) e cada um troca a própria senha em `/conta`. Admin default inicial: `luana` / `matine2026` (trocar em produção). Proteções anti-lockout: não remover/rebaixar o último admin nem a própria conta.

**Migrations (STORY-01-05):** o schema é versionado em `06_APP/migrations/` (scripts `001`–`008`, cada um com `up`/`down`; 007 = `usuarios`, 008 = `config_whatsapp`). `init_db()` aplica só as pendentes via `migrations/runner.py` (atômicas, BEGIN/COMMIT por script). `get_conn()` habilita **WAL** + `foreign_keys=ON`. Banco sem `schema_migrations` é tratado como legado (001–004 marcadas sem re-executar). Nova migration = novo arquivo `NNN_nome.py` com `version` crescente.

---

## Rotas Principais

| Rota | Descrição |
|------|-----------|
| `/login` · `/logout` | Autenticação (público); guard `before_request` protege o resto |
| `/` | Início — upload e consolidação |
| `/resultado` | Resultado da consolidação com filtros |
| `/envio-mensagens` | Wizard de envio (WhatsApp + E-mail) |
| `/base` | Base de inadimplentes persistida |
| `/configuracoes` | Templates, SMTP, Régua, Clientes, **WhatsApp**, Zona de Risco |
| `/crm/gerar-planilha` | Gera XLSX de tagging Kommo (abre a pasta local) |
| `/whatsapp/configurar` | Salva config WhatsApp/Drive + upload do JSON da SA (POST) — STORY-H-01 |
| `/whatsapp/testar` | Testa credencial + acesso à pasta no Drive (AJAX → JSON) — STORY-H-01 |
| `/whatsapp/exportar` | Gera Planilha CRM → `gdrive.upload_xlsx` → registra `envios` (`canal='whatsapp_crm'`) — STORY-H-01 |
| `/ajuda` | Central de Ajuda (índice lateral + conteúdo por tela) |
| `/conta` · `/conta/nome` · `/conta/senha` | Minha conta — edita o próprio nome e senha |
| `/usuarios` (+ `/criar`, `/<id>/senha`, `/<id>/admin`, `/<id>/remover`) | Gestão de usuários (admin) |

Acesso pelo menu do usuário (dropdown no canto superior direito da topbar): Minha conta, Usuários (admin), Central de Ajuda, Sair.

---

## Arquivos Principais do Código

| Arquivo | Responsabilidade |
|---------|-----------------|
| `06_APP/app.py` | Rotas Flask, lógica de negócio, autenticação (Flask-Login), `setup_inicial()` |
| `06_APP/database.py` | SQLite — `get_conn` (WAL+FK), `init_db` (runner), queries, usuários. `DATA_DIR`/`DB_PATH` leem `MATINE_DATA_DIR` (default `C:\MATINE`) |
| `06_APP/migrations/` | Migrations versionadas (`runner.py` + `001`–`008`; 007 = `usuarios`, 008 = `config_whatsapp`) |
| `06_APP/processing.py` | Consolidação, geração de TXT/XLSX/CRM (`gerar_planilha_crm` — base da exportação WhatsApp) |
| `06_APP/gdrive.py` | Upload da planilha no Google Drive (Service Account + Shared Drive, modular p/ OAuth) — STORY-H-01 |
| `06_APP/backup_db.py` | Backup do banco com retenção (WAL-safe, `--keep`) |
| `06_APP/templates/layout.html` | Sidebar, topbar, dropdown do usuário, CSS global (Bootstrap 5.3.3) |
| `06_APP/templates/login.html` | Tela de login standalone (sem sidebar) |
| `06_APP/templates/index.html` | Upload + ações de consolidação |
| `06_APP/templates/resultado.html` | Tabela de resultado com filtros |
| `06_APP/templates/envio_mensagens.html` | Wizard de envio (WhatsApp + E-mail) |
| `06_APP/templates/base.html` | Base persistida com cards de filtro |
| `06_APP/templates/configuracoes.html` | Configurações gerais (inclui a aba **WhatsApp**: Drive + Kommo + Comportamento, com Testar Conexão via AJAX) |
| `06_APP/templates/ajuda.html` | Central de Ajuda |
| `06_APP/templates/usuarios.html` · `conta.html` | Gestão de usuários (admin) · Minha conta |
| `06_APP/conftest.py` · `pytest.ini` · `tests/` | Suíte de testes pytest (banco isolado via `MATINE_DATA_DIR`) |

**Testes:** `cd 06_APP && pip install -r requirements-dev.txt && pytest` (71 testes; nunca tocam produção).

---

## Visão Estratégica do Produto *(decisão 11/06/2026)*

O produto evoluirá das escolas do Edilvo para uma **plataforma SaaS de cobrança de inadimplentes, multi-tenant, cloud-native**.

| Dimensão | Decisão |
|----------|---------|
| Modelo | SaaS — multi-tenant, cloud |
| Cliente zero | Edilvo (INEPROTEC + MATRÍCULA EAD) — laboratório sem cobrança |
| Postura de dev | Cada decisão nas escolas deve ser generalizável — sem gambiarras específicas do Synapta |
| Nomenclatura futura | "aluno" → "devedor/cliente"; templates educacionais → exemplos padrão |

**Roadmap de evolução arquitetural (v2):**
- SQLite → PostgreSQL
- `C:\MATINE\` → storage cloud (S3 ou similar por tenant)
- Flask local Windows → deploy cloud (Railway / Render / AWS — TBD)
- Keyring Windows → vault cloud
- 2 empresas hardcoded → N tenants
- Fonte Synapta → importação genérica com mapeamento de colunas configurável

---

## Integração WhatsApp — Decisões *(11/06/2026)*

**Fluxo escolhido:**
```
App gera planilha XLSX → sobe no Google Drive (pasta configurada) →
Kommo lê via Make ou integração nativa Google Sheets →
dispara WhatsApp pelo número conectado ao Kommo →
tipo de mensagem definido pela tag_crm
```

**Formato da planilha — DECIDIDO (15/06/2026):** reaproveitar a **Planilha CRM** existente (`proc.gerar_planilha_crm`, botão "Planilha CRM" em Envio de Mensagens). XLSX `CRM_{empresa}_{data}.xlsx` em `C:\MATINE\crm-exports\`, com 2 abas:
- `Inadimplentes`: Nome · CPF · Telefone · E-mail · Categoria · Dias Atraso · Valor (R$) · **Tag CRM** (vem do template que casa com os dias de atraso via `_encontrar_template_crm`)
- `Saídos_Quitados`: Nome · CPF · Telefone · E-mail · Status · Ação CRM (`REMOVER_TAG`)

O Kommo lê a aba `Inadimplentes` — `Telefone` + `Tag CRM` são o essencial para o disparo. Não criar formato novo.

**Tag CRM:** já existe campo `tag_crm` por template. Tags exemplo: `INADIMPLENTE_NOVO`, `INADIMPLENTE_REGUA`, `INADIMPLENTE_30DIAS`.

**Auth Google Drive — DECIDIDO (15/06/2026):** **Service Account** (JSON) + **Shared Drive** (Edilvo tem Google Workspace, domínio `@ineprotec.com.br`). No Shared Drive os arquivos pertencem à organização (não à SA) → elimina `storageQuotaExceeded`. SA entra como membro Gerenciador de conteúdo; chamadas da API com `supportsAllDrives=True`. JSON guardado em `C:\MATINE\secrets\` (fora do git e do banco). OAuth fica para a v2 SaaS (cada tenant conecta o próprio Drive); `gdrive.py` deve ser **modular** para a troca SA→OAuth ser barata.

**Aba de Configuração WhatsApp** — ✅ **IMPLEMENTADA (Onda 2, 15/06/2026)**. Seção em Configurações (migration 008, config por empresa):
- Bloco Google Drive: upload do JSON da SA (validado), ID da pasta (no Shared Drive), template do nome do arquivo, botão Testar Conexão (AJAX → `/whatsapp/testar`)
- Bloco Kommo: URL do webhook ou ID do pipeline
- Bloco Comportamento: toggle de exportação automática (default OFF — geração **sob demanda** via botão em Envio de Mensagens)
- Salva via `POST /whatsapp/configurar`; campo de credencial vazio preserva a credencial atual (espelha a senha SMTP)

**Fluxo de exportação** — ✅ **IMPLEMENTADO (Onda 2)**: botão **"Exportar para WhatsApp"** em Envio de Mensagens (só aparece com Drive configurado) → `POST /whatsapp/exportar` → `proc.gerar_planilha_crm` → `gdrive.upload_xlsx` (cria/substitui o arquivo do dia) → registra um `envios` por inadimplente.

**Canal registrado na tabela `envios`:** `canal='whatsapp_crm'`

**Estado da STORY-H-01:** código completo (Onda 1 backend + Onda 2 UI/fluxo), status **InReview**. Falta o onboarding real (criar Service Account + Shared Drive, testar conexão/exportação, validar ponta a ponta com o Kommo) → QA gate fecha a story. Commits no remoto: `440ccfc` (feat Onda 2). Detalhes operacionais em `PLANO_DE_ACAO.md`.

---

## Problemas Conhecidos e Soluções

| # | Sintoma | Solução | Status |
|---|---------|---------|--------|
| 1 | Separador CSV variável (`,` ou `;`) | Loop testa múltiplos separadores | ✅ |
| 2 | Linha de cabeçalho extra no Synapta | Testa skip=[0,1] | ✅ |
| 3 | Valores em formato brasileiro `R$ 1.024,62` | `converter_valor()` | ✅ |
| 4 | CPF perde zeros à esquerda | `.str.zfill(11)` | ✅ |
| 5 | Alunos sem cadastro não aparecem no resultado | Flash warning pós-consolidação | ✅ |
| 6 | Gênero errado (sr. Vanessa) | `detectar_tratamento()` por heurística | ✅ |
| 7 | Renegociados aparecem como Quitados | Campo `status` no banco + revisão manual | ✅ parcial |
