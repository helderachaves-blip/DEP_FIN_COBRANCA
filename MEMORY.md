# MEMORY — MAT-INE Inadimplência 2026

> Contexto permanente do projeto. Atualizar apenas quando algo estrutural mudar.
> Última atualização: 10/06/2026

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

**Autenticação (STORY-01-06 → STORY-MULTIUSUARIO):** multi-usuário via tabela `usuarios`. Login/`user_loader` consultam o banco; senha sempre hash pbkdf2. O `.env` (`APP_USUARIO`/`APP_SENHA`) serve **só como semente** do 1º admin na tabela vazia — depois disso a gestão é pela tela `/usuarios` (admin) e cada um troca a própria senha em `/conta`. Admin default inicial: `luana` / `matine2026` (trocar em produção). Proteções anti-lockout: não remover/rebaixar o último admin nem a própria conta.

**Migrations (STORY-01-05):** o schema é versionado em `06_APP/migrations/` (scripts `001`–`007`, cada um com `up`/`down`; 007 = tabela `usuarios`). `init_db()` aplica só as pendentes via `migrations/runner.py` (atômicas, BEGIN/COMMIT por script). `get_conn()` habilita **WAL** + `foreign_keys=ON`. Banco sem `schema_migrations` é tratado como legado (001–004 marcadas sem re-executar). Nova migration = novo arquivo `NNN_nome.py` com `version` crescente.

---

## Rotas Principais

| Rota | Descrição |
|------|-----------|
| `/login` · `/logout` | Autenticação (público); guard `before_request` protege o resto |
| `/` | Início — upload e consolidação |
| `/resultado` | Resultado da consolidação com filtros |
| `/envio-mensagens` | Wizard de envio (WhatsApp + E-mail) |
| `/base` | Base de inadimplentes persistida |
| `/configuracoes` | Templates, SMTP, Régua, Clientes, Zona de Risco |
| `/crm/gerar-planilha` | Gera XLSX de tagging Kommo |
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
| `06_APP/migrations/` | Migrations versionadas (`runner.py` + `001`–`007`; 007 = `usuarios`) |
| `06_APP/processing.py` | Consolidação, geração de TXT/XLSX/CRM |
| `06_APP/backup_db.py` | Backup do banco com retenção (WAL-safe, `--keep`) |
| `06_APP/templates/layout.html` | Sidebar, topbar, dropdown do usuário, CSS global (Bootstrap 5.3.3) |
| `06_APP/templates/login.html` | Tela de login standalone (sem sidebar) |
| `06_APP/templates/index.html` | Upload + ações de consolidação |
| `06_APP/templates/resultado.html` | Tabela de resultado com filtros |
| `06_APP/templates/envio_mensagens.html` | Wizard de envio (WhatsApp + E-mail) |
| `06_APP/templates/base.html` | Base persistida com cards de filtro |
| `06_APP/templates/configuracoes.html` | Configurações gerais |
| `06_APP/templates/ajuda.html` | Central de Ajuda |
| `06_APP/templates/usuarios.html` · `conta.html` | Gestão de usuários (admin) · Minha conta |
| `06_APP/conftest.py` · `pytest.ini` · `tests/` | Suíte de testes pytest (banco isolado via `MATINE_DATA_DIR`) |

**Testes:** `cd 06_APP && pip install -r requirements-dev.txt && pytest` (52 testes; nunca tocam produção).

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

**Estrutura da planilha (a validar com Kommo):**

| telefone | nome | tag_crm | empresa | categoria | vencimento | valor |
|----------|------|---------|---------|-----------|------------|-------|
| 5511... | João | INADIMPLENTE_REGUA | INEPROTEC | Régua | 01/06/2026 | R$350 |

**Tags definidas:** `INADIMPLENTE_NOVO`, `INADIMPLENTE_REGUA`, `INADIMPLENTE_30DIAS`

**Aba de Configuração WhatsApp** (nova seção em Configurações — migration 008):
- Bloco Google Drive: Service Account JSON ou OAuth, ID da pasta, nome do arquivo, botão Testar Conexão
- Bloco Kommo: URL do webhook ou ID do pipeline, tag CRM padrão
- Bloco Comportamento: geração **sob demanda** via botão em Envio de Mensagens (não automático)

**Canal registrado na tabela `envios`:** `canal='whatsapp_crm'`

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
