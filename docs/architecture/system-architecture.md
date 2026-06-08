# System Architecture --- MAT-INE Inadimplencia 2026

**Autor:** Aria (@architect) --- Brownfield Discovery Fase 1
**Data:** 2026-06-04
**Versao analisada:** App Web Flask (Fases A-G concluidas, Fase H planejada)
**Arquivo principal:** 06_APP/app.py

---

## 1. Visao Geral do Sistema

O MAT-INE Inadimplencia 2026 e uma aplicacao web local (single-user, localhost-only) para gestao
operacional de cobancas de faturas vencidas. Atende duas empresas: **Ineprotec** e **Matricula EaD**.

**Fluxo principal de uso diario (operadora Luana):**

    Synapta (ERP) -> exportacao CSV manual
        -> Upload via browser (localhost:5000)
        -> Consolidacao pandas (join vencidos + cadastro alunos)
        -> Estado salvo em pickle (C:\MATINE\estado\)
        -> Geracao de relatorios .txt/.xlsx (C:\MATINEelatorios\)
        -> Wizard WhatsApp (copiar mensagens formatadas)
        -> Envio e-mail em lote via SMTP
        -> Atualizacao da base SQLite (C:\MATINEanco\inadimplencia.db)

**Objetivo do negocio:** Reduzir trabalho de cobranca de 2,5-4h/dia para ~15 min/dia.

**Usuarios:**
- Luana (operadora diaria, nao tecnica --- acessa via ABRIR CONSOLIDADOR WEB.bat)
- Helder (TI/arquitetura)
- Edilvo (gerente)

---

## 2. Stack Tecnologico

### Backend

| Componente | Versao Declarada | Versao em uso (pip) | Notas |
|------------|-----------------|---------------------|-------|
| Python | 3.14 | 3.14 | C:\Users\Lorena\AppData\Local\Programs\Python\Python314\ |
| Flask | >=3.1.0 (06_APP/requirements.txt) | Nao fixada | Sem pin de versao exata |
| pandas | >=3.0.0 (06_APP/requirements.txt) | 3.0.3 (MEMORY.md) | requirements.txt raiz tem pandas==2.1.0 (conflito) |
| openpyxl | >=3.1.0 (06_APP/requirements.txt) | 3.1.5 (MEMORY.md) | Leitura/escrita .xlsx |
| SQLite | embutido (stdlib) | --- | Banco de producao |
| smtplib | stdlib | --- | Envio de e-mail |
| pickle | stdlib | --- | Persistencia de estado de consolidacao |

### Frontend

| Componente | Versao | Carregamento |
|------------|--------|--------------|
| Bootstrap | 5.3.3 | CDN (jsdelivr.net) --- sem fallback local |
| Bootstrap Icons | 1.11.3 | CDN (jsdelivr.net) |
| JavaScript inline | --- | Sem framework (vanilla JS nos templates) |

### Infraestrutura de execucao

- Servidor: Flask dev server (app.run(debug=False, host=127.0.0.1, port=5000))
- Launcher: .bat com caminho Python hardcoded (C:\Users\Lorena\AppData\Local\Programs\Python\Python314\python.exe)
- Sistema operacional: Windows 10 Pro
- Ambiente: localhost exclusivo (sem deploy em servidor)

---

## 3. Estrutura de Modulos

    MAT-INE - INADIMPLENCIA - 2026/
    +-- 06_APP/                     <- aplicacao web Flask (ativa)
    |   +-- app.py                  <- rotas Flask + helpers (~970 linhas)
    |   +-- database.py             <- acesso SQLite + migracoes inline (~550 linhas)
    |   +-- processing.py           <- logica pandas + geracao de relatorios (~480 linhas)
    |   +-- templates/              <- Jinja2 HTML
    |   |   +-- layout.html         <- base (sidebar, topbar, CSS)
    |   |   +-- index.html          <- tela inicial (upload + status)
    |   |   +-- resultado.html      <- tabela consolidada
    |   |   +-- base.html           <- gestao base inadimplentes
    |   |   +-- configuracoes.html  <- templates mensagens + SMTP (~29KB)
    |   |   +-- wizard_whatsapp.html<- wizard envio (~21KB)
    |   +-- static/                 <- apenas logos PNG (2 arquivos)
    |   +-- uploads/                <- uploads temporarios (nao commitados)
    |   +-- requirements.txt        <- dependencias app web
    +-- 01_SCRIPTS/
    |   +-- inadimplencia_app.py    <- app desktop tkinter legada (~870 linhas)
    +-- BASE DE DADOS/              <- arquivos fonte CSV + banco legado + inadimplencia.db
    +-- ABRIR CONSOLIDADOR WEB.bat  <- launcher web
    +-- ABRIR CONSOLIDADOR.bat      <- launcher desktop (legado)
    +-- requirements.txt            <- raiz --- versoes ANTIGAS (conflito com 06_APP/requirements.txt)
    +-- docs/architecture/          <- criado nesta analise

OBSERVACAO CRITICA: A app web define DATA_DIR = Path(r C:\MATINE) como raiz de dados em producao,
criada automaticamente no startup. O repositorio tambem contem BASE DE DADOS/inadimplencia.db
(copia de desenvolvimento), criando risco de dois bancos divergentes silenciosamente.

---

## 4. Arquitetura de Rotas (Request Flow)

### Mapa de rotas completo

| Metodo | Rota | Funcao | Responsabilidade |
|--------|------|--------|-----------------|
| GET | / | index | Dashboard principal --- status base + upload |
| POST | /upload | upload | Salva arquivo CSV/XLSX na pasta uploads |
| POST | /consolidar | consolidar | Processa pandas + salva estado pickle |
| GET | /resultado | resultado | Exibe tabela consolidada |
| POST | /gerar-relatorio | gerar_relatorio | Gera .txt/.xlsx por template |
| POST | /atualizar-base | atualizar_base | Diff base SQLite + relatorios diff |
| GET | /base | base | Lista inadimplentes na base |
| POST | /base/limpar | limpar_base | Apaga toda a base da empresa |
| POST | /base/status | atualizar_status | Muda status INADIMPLENTE/QUITADO/RENEGOCIADO |
| GET | /configuracoes | configuracoes | Templates mensagens + SMTP |
| POST | /configuracoes/template/novo | template_novo | Cria template mensagem |
| POST | /configuracoes/template/<tid>/editar | template_editar | Edita template |
| POST | /configuracoes/template/<tid>/excluir | template_excluir | Exclui template |
| GET | /abrir-relatorios | abrir_relatorios | os.startfile() --- abre pasta no Explorer |
| GET | /limpar | limpar | Limpa estado pickle da sessao |
| GET | /empresa/<nome> | trocar_empresa | Altera empresa ativa na sessao Flask |
| GET | /wizard-whatsapp | wizard_whatsapp | Tela wizard de envio |
| POST | /whatsapp/marcar-enviado | whatsapp_marcar_enviado | AJAX --- registra envio individual |
| POST | /whatsapp/marcar-todos | whatsapp_marcar_todos | Marca todos como enviados |
| POST | /email/configurar | email_configurar | Salva configuracao SMTP |
| POST | /email/testar | email_testar | Testa conexao SMTP |
| POST | /email/assunto/<tid> | email_assunto | Salva assunto por template |
| POST | /email/enviar-aluno | email_enviar_aluno | AJAX --- envia e-mail individual |
| POST | /email/enviar-todos | email_enviar_todos | Envio em lote SMTP |

### Request Flow principal

    Browser -> Flask route -> carrega estado pickle -> operacao pandas/db -> flash message -> redirect

Padrao PRG (Post-Redirect-Get) usado consistentemente para evitar reenvio de formulario.
AJAX (retorna JSON) apenas em /whatsapp/marcar-enviado e /email/enviar-aluno.


---

## 5. Gestao de Estado e Sessao

### Estado de empresa (Flask session cookie)

- Chave: session[empresa] --- valores: INEPROTEC | MATRICULAEAD
- Assinado pelo secret_key hardcoded: matine2026-inadimplencia (app.py linha 38)
- Lido via get_empresa() em todas as rotas
- Injetado em todos os templates via @app.context_processor

### Estado de consolidacao (pickle em disco)

Localizacao: C:\MATINE\estado\estado_{empresa}.pkl

Conteudo serializado:
- consolidado: pd.DataFrame --- resultado do join vencidos+alunos
- stats: dict --- totais por categoria e valores agregados
- avencer: pd.DataFrame --- boletos a vencer (opcional, Fase E)
- stats_avencer: dict --- totais a vencer

Ciclo de vida: criado em /consolidar, consumido em /resultado, /gerar-relatorio,
/atualizar-base, /wizard-whatsapp. Apagado em /limpar e no inicio de cada nova consolidacao.

### Persistencia de dados (SQLite)

Localizacao: C:\MATINE\banco\inadimplencia.db

| Tabela | PK | Descricao |
|--------|-----|-----------|
| inadimplentes | (cpf, empresa) | Base historica de inadimplentes |
| templates | id | Mensagens de cobranca configuaveis por empresa |
| historico_atualizacoes | id | Log de cada atualizacao da base |
| envios | id | Rastreio de envios por canal/CPF/data/empresa |
| config_email | id, UNIQUE empresa | Configuracao SMTP por empresa |

---

## 6. Dependencias Externas e Integracoes

### Integracoes atuais

| Sistema | Tipo | Mecanismo | Observacoes |
|---------|------|-----------|-------------|
| Synapta (ERP) | Exportacao manual | CSV/XLSX baixado pelo usuario | Sem API. 3 tipos: vencidos, a-vencer, alunos |
| SMTP (e-mail) | Envio ativo | smtplib stdlib | Configuravel por empresa. TLS/SSL suportado |
| Sistema de arquivos Windows | Abertura de pasta | os.startfile() | Acoplado ao Windows |
| Bootstrap/Icons | Front-end | CDN jsdelivr.net | Sem fallback --- requer internet |

### Integracoes planejadas (Fase H --- nao implementadas)

| Sistema | Tipo | Status |
|---------|------|--------|
| WhatsApp via WAHA/Twilio | Envio automatico | Planejado |
| Synapta API | Link de pagamento dinamico | Depende de API externa |
| Kommo CRM | Tagging automatico | Planejado |
| Agendador | Execucao automatica diaria/semanal | Planejado |

---

## 7. Configuracoes e Ambiente

### Configuracoes hardcoded em codigo-fonte

| Arquivo | Linha | Valor hardcoded | Impacto |
|---------|-------|-----------------|---------|
| app.py | 27 | DATA_DIR = Path(C:\MATINE) | Todos os dados em caminho fixo Windows |
| app.py | 38 | app.secret_key = matine2026-inadimplencia | Chave de sessao em texto plano |
| database.py | 11 | DB_PATH = Path(C:\MATINE\banco\inadimplencia.db) | Banco SQLite em caminho fixo |
| ABRIR CONSOLIDADOR WEB.bat | ~8 | C:\Users\Lorena\AppData\...\python.exe | Path Python para usuario especifico |
| app.py | 961 | host=127.0.0.1, port=5000 | Porta sem configuracao externa |

### Dois requirements.txt conflitantes

| Arquivo | pandas | openpyxl | Flask |
|---------|--------|----------|-------|
| requirements.txt (raiz) | ==2.1.0 | ==3.11.0 | ausente |
| 06_APP/requirements.txt | >=3.0.0 | >=3.1.0 | >=3.1.0 |

O requirements.txt raiz e legado (app tkinter) e nao corresponde ao ambiente da app web.

### Estrutura de dados em producao

    C:\MATINE    +-- uploads/{EMPRESA}/{tipo}/              (vencidos, avencer, alunos)
    +-- relatorios/{EMPRESA}/{ano}/{mes}/{dia}/ (relatorios gerados)
    +-- estado/estado_{empresa}.pkl            (estado de consolidacao)
    +-- banco/inadimplencia.db                 (banco SQLite)
    +-- logs/app_web.log


---

## 8. Debitos Tecnicos Identificados

### 8.1 Criticos

[SEC-01] Secret key de sessao hardcoded em texto plano
- Arquivo: app.py, linha 38: app.secret_key = matine2026-inadimplencia
- Qualquer pessoa com acesso ao repositorio pode forjar cookies de sessao
- Correcao: os.environ.get(FLASK_SECRET_KEY) + secrets.token_hex(32) no .env

[SEC-02] Senha SMTP armazenada em texto plano no SQLite
- database.py: tabela config_email, coluna smtp_senha sem criptografia
- Qualquer acesso ao .db expoe a senha do e-mail corporativo
- Correcao: cryptography.fernet ou Windows DPAPI via pywin32

[SEC-03] Ausencia total de autenticacao/autorizacao
- app.py: nenhuma rota protegida por login
- Rota /base/limpar apaga toda a base sem verificacao de identidade
- Risco atual: baixo (127.0.0.1 only). Risco com Fase H em rede: alto
- Correcao: flask-login com usuario unico via variavel de ambiente

[SEC-04] Pickle para persistencia - risco de deserializacao arbitraria
- app.py, linhas 130 e 147: _salvar_estado() e _carregar_estado()
- Arquivo .pkl substituido por agente malicioso executa codigo arbitrario
- Correcao: JSON para stats + Parquet para DataFrames; remover import pickle

---

### 8.2 Altos

[ARCH-01] Dois caminhos de dados com risco de divergencia silenciosa
- App web usa C:/MATINE/banco/inadimplencia.db (database.py linha 11)
- Repositorio contem BASE DE DADOS/inadimplencia.db (copia de desenvolvimento)
- Sem documentacao de qual e o banco canonico
- Correcao: Variavel de ambiente MATINE_DATA_DIR; documentar banco canonico

[ARCH-02] God function init_db() com 163 linhas de migracoes acumulativas
- database.py, linhas 135-298: migracoes das Fases C, D, E, F, G empilhadas
- Executada a cada startup com multiplos PRAGMA table_info condicionais
- Sem controle de versao; falha parcial deixa banco inconsistente
- Correcao: Tabela schema_version + scripts numerados em migrations/

[ARCH-03] Acoplamento ao Windows via os.startfile() em app.py linha 571
- Nao funciona em Linux/Mac; bloqueia eventual deploy em servidor
- Correcao: Rota de download HTTP /download-relatorios

[ARCH-04] app.py monolitico com 970+ linhas sem separacao de camadas
- Logica de negocio misturada com rotas HTTP
- _enviar_email_smtp(), _formatar_mensagem_wizard(), _encontrar_template(),
  _salvar_estado() pertencem a camadas de servico, nao ao arquivo de rotas
- Correcao: services/email_service.py, services/estado_service.py,
  services/template_service.py

[QUAL-01] Zero testes automatizados para a aplicacao Python
- Nenhum test_*.py, pytest.ini, conftest.py na aplicacao Flask
- Funcoes criticas sem cobertura: consolidar(), _ler_csv(), _converter_valor(),
  salvar_base(), _encontrar_template()
- Correcao: 06_APP/tests/ com pytest; priorizar consolidar() e _converter_valor()

[QUAL-02] Montagem de e-mail duplicada em dois locais
- app.py linha 718: _enviar_email_smtp() - monta MIMEMultipart
- app.py linha 899: _send_one() em email_enviar_todos - monta MIMEMultipart novamente
- Correcao: Extrair para _build_mime_message() reutilizada em ambas

---

### 8.3 Medios

[CFG-01] Dois requirements.txt com versoes conflitantes
- requirements.txt raiz: pandas==2.1.0, openpyxl==3.11.0 (legado tkinter, sem Flask)
- 06_APP/requirements.txt: flask>=3.1.0, pandas>=3.0.0 (sem pins exatos)
- Correcao: Renomear raiz para requirements-legacy-desktop.txt;
  adicionar pins exatos no 06_APP/requirements.txt

[CFG-02] PATH Python hardcoded para usuario Lorena no launcher web
- ABRIR CONSOLIDADOR WEB.bat linha 8: C:/Users/Lorena/AppData/Local/Programs/Python/Python314/python.exe
- Launcher legado ABRIR CONSOLIDADOR.bat usa %LOCALAPPDATA% corretamente
- Correcao: Substituir por %LOCALAPPDATA%/Programs/Python/Python314/python.exe

[QUAL-03] Dead code: gerar_txt() e gerar_xlsx() legadas em processing.py
- Substituidas por gerar_txt_template() e gerar_xlsx_template() mas nao removidas
- Usam schema antigo de 3 templates fixos (incompativel com sistema atual)
- Correcao: Remover (grep confirma ausencia de chamadas em app.py)

[QUAL-04] Ausencia de indices no banco SQLite (nenhum CREATE INDEX nas 5 tabelas)
- get_envios_hoje() usa LIKE com wildcard inicial em data_envio TEXT -- nao indexavel
- Impacto atual irrelevante (<1000 inadimplentes); escala com automacao em Fase H
- Correcao: CREATE INDEX idx_envios ON envios(empresa, data_envio);
  migrar data_envio para ISO-8601

[QUAL-05] detectar_tratamento() heuristica fragil de genero (processing.py linhas 13-19)
- Nomes terminados em a -> Sra.; excecoes hardcoded em listas pequenas
- Falha para Lucas, Dantas, Tatiana, Andrea; sem testes cobrindo edge cases

[QUAL-06] Validacao de upload somente por extensao (app.py, rota /upload)
- Arquivo corrompido com extensao valida falha silenciosamente na consolidacao
- Impacto baixo atualmente (localhost, operadora conhecida)

[QUAL-07] _carregar_estado() silencia erros de corrupcao de pickle (app.py linha 167)
- except Exception: return None, None, None, None
- Pickle corrompido retorna estado vazio sem log ou alerta ao usuario
- Correcao: _log() antes do return None

---

### 8.4 Baixos

[DOC-01] 06_APP/README.md desatualizado: descreve app tkinter, nao app web Flask atual

[DOC-02] Imports nao utilizados em app.py
- Linha 6: import json (nao aparece diretamente, apenas via jsonify do Flask)
- Linha 9: import shutil (nao aparece em nenhuma chamada atual)
- Correcao: Remover com autoflake + isort

[DOC-03] get_templates() em database.py linha 300 provavelmente dead code
- app.py usa exclusivamente get_templates_completo(); confirmar e remover

[PERF-01] Template lookup em loop .iterrows() (resultado() e wizard_whatsapp())
- Operacao em memoria, aceitavel com <500 alunos; monitorar em Fase H (>1000)

[PERF-02] Bootstrap/Icons de CDN sem fallback offline (layout.html linhas 7-8 e 259)
- Interface fica sem estilo sem internet (possivel em ambiente corporativo)
- Correcao: Copiar para 06_APP/static/vendor/ ou usar SRI + fallback local

---

## 9. Perguntas para @data-engineer e @ux-design-expert

### Para @data-engineer

1. Schema de migracoes: init_db() tem 163 linhas de migracoes acumulativas executadas
   a cada startup (Fases C-G inline). Alembic e justificavel para SQLite mono-arquivo,
   ou uma tabela schema_version simples com scripts numerados resolve?

2. Indices e formato de data: get_envios_hoje() usa WHERE data_envio LIKE com wildcard
   inicial em TEXT -- nao indexavel. Migrar para ISO-8601 DATETIME + indice composto?
   Qual o impacto nos dados historicos existentes?

3. Dois bancos SQLite: BASE DE DADOS/inadimplencia.db (repositorio) e
   C:/MATINE/banco/inadimplencia.db (producao). Sao o mesmo arquivo? Como garantir
   banco canonico unico sem risco de divergencia silenciosa?

4. Criptografia da senha SMTP: smtp_senha em texto plano no SQLite. Mecanismo adequado
   no Windows sem servidor externo: cryptography.fernet com chave de variavel de ambiente?
   Windows DPAPI via pywin32?

5. Escalabilidade do pickle: Fase H com automacao pode ter multiplas instancias.
   Pickle por empresa nao suporta concorrencia. Substituto: SQLite com tabela sessions?
   Arquivos JSON atomicos? Redis e necessario neste contexto operacional?

### Para @ux-design-expert

1. Wizard WhatsApp - dois modos: Fluxo atual e manual (copia por copia). Fase H
   prevee envio automatico (WAHA/Twilio). Como redesenhar para suportar ambos os modos
   sem confundir a operadora Luana (nao-tecnica)?

2. Multi-empresa - risco de contexto errado: Trocar empresa muda contexto global sem
   indicador visual permanente. Risco de enviar cobancas pela empresa errada e real.
   Tratamento visual sugerido: borda colorida? Banner de alerta? Cor da topbar por empresa?

3. configuracoes.html com 29KB e 5 abas pesadas: Faz sentido dividir em sub-rotas
   (/configuracoes/mensagens, /configuracoes/email)? Qual o impacto na navegacao da Luana?

4. Mensagens de erro para operadora nao-tecnica: Hoje chegam com excecao Python crua
   (ex: KeyError CPF sem mask). Como redesenhar para mensagens acionaveis, ex:
   O arquivo de Vencidos nao possui a coluna esperada. Verifique se exportou do Synapta.

5. Responsividade 1366x768: Sidebar fixa de 230px (~17% da largura em monitores comuns).
   Tabela de resultado e wizard ficam comprimidos. Avaliar sidebar colapsavel ou nav adaptativo?

---

Documento gerado por Aria (@architect) -- Brownfield Discovery Fase 1
Proximos passos:
  @data-engineer: Fase 2 -- DB-AUDIT.md + SCHEMA.md
  @ux-design-expert: Fase 3 -- frontend-spec.md
