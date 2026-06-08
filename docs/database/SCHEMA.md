# Database Schema — MAT-INE Inadimplencia 2026

**Arquivo de banco:** `C:\MATINE\banco\inadimplencia.db`
**Engine:** SQLite 3
**Modulo de acesso:** `06_APP/database.py`
**Multi-empresa:** Sim - discriminador `empresa` presente em todas as tabelas operacionais
**Empresas suportadas:** `INEPROTEC`, `MATRICULAEAD`

---

## Tabelas

### inadimplentes

Tabela central da aplicacao. Armazena o cadastro atual de alunos inadimplentes por empresa.

| Coluna             | Tipo    | Constraints                              | Descricao |
|--------------------|---------|------------------------------------------|-----------|
| cpf                | TEXT    | NOT NULL, PK parte 1                     | CPF do aluno, zero-padded 11 chars |
| empresa            | TEXT    | NOT NULL, PK parte 2, DEFAULT INEPROTEC  | Discriminador multi-tenant |
| aluno              | TEXT    | NOT NULL                                 | Nome completo do aluno |
| telefone           | TEXT    | -                                        | Telefone (pode ser NULL) |
| email              | TEXT    | -                                        | E-mail (pode ser NULL) |
| qtd_boletos        | INTEGER | -                                        | Quantidade de boletos em aberto |
| total              | REAL    | -                                        | Valor total em aberto (ponto flutuante) |
| ultimo_vencimento  | TEXT    | -                                        | Data ultimo vencimento (DD/MM/YYYY como TEXT) |
| dias_atraso        | INTEGER | -                                        | Dias de atraso calculados externamente |
| categoria          | TEXT    | -                                        | A Vencer, Novos Inadimplentes, Regua, Acima 30 Dias |
| status             | TEXT    | DEFAULT INADIMPLENTE                     | Status manual: INADIMPLENTE, NEGOCIANDO, etc. |
| data_entrada       | TEXT    | -                                        | Data de inclusao na base (DD/MM/YYYY) |
| data_atualizacao   | TEXT    | -                                        | Ultima atualizacao (DD/MM/YYYY HH:MM:SS) |
| qtd_cobranca       | INTEGER | DEFAULT 0                                | Contador de cobrancas enviadas (adicionado Fase E) |

**Chave primaria composta:** (cpf, empresa)

**Historico de migracoes inline:**
- Schema original: sem PK, sem coluna empresa (Fases A/B)
- Fase C: renomeacao de categorias A -> Regua, B -> Acima 30 Dias  (database.py ln 173-180)
- Fase D: recriacao com PK composta (cpf, empresa) via inadimplentes_v2  (database.py ln 183-203)
- Fase E: ALTER TABLE ADD COLUMN qtd_cobranca INTEGER DEFAULT 0  (database.py ln 205-208)

---

### templates

Armazena os templates de mensagens de cobranca (WhatsApp e e-mail) por empresa e categoria.

| Coluna          | Tipo    | Constraints               | Descricao |
|-----------------|---------|---------------------------|-----------|
| id              | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador unico |
| categoria       | TEXT    | NOT NULL                  | A Vencer, Novos Inadimplentes, Regua, Acima 30 Dias, Custom |
| titulo          | TEXT    | NOT NULL                  | Titulo descritivo do template |
| conteudo        | TEXT    | NOT NULL                  | Corpo da mensagem com placeholders {NOME}, {TRATAMENTO}, {DATA_VENCIMENTO}, {LINK_PAGAMENTO} |
| ativo           | INTEGER | DEFAULT 1                 | Flag booleano 0/1 |
| empresa         | TEXT    | NOT NULL DEFAULT INEPROTEC| Discriminador multi-tenant (adicionado Fase D) |
| dias_de         | INTEGER | -                         | Inicio do intervalo de dias de atraso (NULL = A Vencer) |
| dias_ate        | INTEGER | -                         | Fim do intervalo (NULL = sem limite superior) |
| assunto_email   | TEXT    | -                         | Assunto do e-mail (adicionado Fase G) |

**Chave primaria:** id

**Historico de migracoes inline:**
- Fase D: ALTER TABLE ADD COLUMN empresa TEXT NOT NULL DEFAULT INEPROTEC  (database.py ln 209-211)
- Fase F: ALTER TABLE ADD COLUMN dias_de INTEGER / dias_ate INTEGER  (database.py ln 213-228)
- Fase G: ALTER TABLE ADD COLUMN assunto_email TEXT  (database.py ln 257-259)

---

### envios

Registro historico de todos os envios de mensagens realizados pela aplicacao.

| Coluna            | Tipo    | Constraints               | Descricao |
|-------------------|---------|---------------------------|-----------|
| id                | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador unico |
| cpf               | TEXT    | NOT NULL                  | CPF do aluno destinatario |
| empresa           | TEXT    | NOT NULL                  | Empresa remetente |
| canal             | TEXT    | NOT NULL                  | Canal: whatsapp, email, etc. |
| template_titulo   | TEXT    | -                         | Titulo do template utilizado |
| data_envio        | TEXT    | NOT NULL                  | Data/hora do envio (DD/MM/YYYY HH:MM:SS) |
| status            | TEXT    | DEFAULT enviado           | Status do envio |

**Chave primaria:** id
**Criada em:** Fase F/G  (database.py ln 239-248)

---

### config_email

Configuracoes SMTP por empresa para envio de e-mails.

| Coluna           | Tipo    | Constraints               | Descricao |
|------------------|---------|---------------------------|-----------|
| id               | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador unico |
| empresa          | TEXT    | NOT NULL, UNIQUE          | Empresa — um registro por empresa |
| smtp_host        | TEXT    | DEFAULT ''                | Servidor SMTP |
| smtp_port        | INTEGER | DEFAULT 587               | Porta SMTP |
| smtp_usuario     | TEXT    | DEFAULT ''                | Usuario SMTP |
| smtp_senha       | TEXT    | DEFAULT ''                | Senha SMTP em texto plano |
| smtp_from_name   | TEXT    | DEFAULT ''                | Nome exibido no remetente |
| smtp_tls         | INTEGER | DEFAULT 1                 | Usar TLS (0/1) |

**Chave primaria:** id
**Unique constraint:** empresa
**Criada em:** Fase F/G  (database.py ln 249-257)

---

### historico_atualizacoes

Log das operacoes de carga/atualizacao da base de inadimplentes.

| Coluna        | Tipo    | Constraints               | Descricao |
|---------------|---------|---------------------------|-----------|
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador unico |
| data          | TEXT    | NOT NULL                  | Data/hora da atualizacao (DD/MM/YYYY HH:MM:SS) |
| total_base    | INTEGER | -                         | Total de registros na base apos a operacao |
| novos         | INTEGER | -                         | Quantidade de novos inadimplentes incluidos |
| saidos        | INTEGER | -                         | Quantidade removidos |
| continuam     | INTEGER | -                         | Quantidade que permaneceu |
| empresa       | TEXT    | NOT NULL DEFAULT INEPROTEC| Discriminador multi-tenant (adicionado pos-criacao) |

**Chave primaria:** id

**Historico de migracoes inline:**
- Fase D: ALTER TABLE ADD COLUMN empresa TEXT NOT NULL DEFAULT INEPROTEC  (database.py ln 231-233)

---

## Relacionamentos

O schema **nao possui foreign key constraints declaradas**. Os relacionamentos logicos existem mas sao aplicados apenas em nivel de aplicacao:

| Tabela origem           | Coluna          | Tabela destino | Coluna        | Tipo de relacao                      | Enforced? |
|-------------------------|-----------------|----------------|---------------|--------------------------------------|-----------|
| envios                  | cpf + empresa   | inadimplentes  | cpf + empresa | N:1 muitos envios por inadimplente   | NAO       |
| envios                  | template_titulo | templates      | titulo        | N:1 muitos envios por template       | NAO       |
| historico_atualizacoes  | empresa         | -              | -             | Vinculo logico a empresa             | NAO       |
| templates               | empresa         | -              | -             | Vinculo logico a empresa             | NAO       |
| config_email            | empresa         | -              | -             | Vinculo logico a empresa             | NAO       |

Observacao: a coluna `empresa` em todas as tabelas deveria referenciar um enum ou tabela `empresas`,
mas nao existe tabela de empresas. A validacao e feita pela constante EMPRESAS no codigo Python (ln 13 de database.py).

---

## Indices

### Indices declarados

Nenhum indice explicito e criado em database.py. Apenas as constraints de chave primaria geram indices implicitos:

| Tabela                  | Indice implicito | Colunas        |
|-------------------------|-----------------|----------------|
| inadimplentes           | PK composta     | (cpf, empresa) |
| templates               | PK              | id             |
| envios                  | PK              | id             |
| config_email            | PK              | id             |
| config_email            | UNIQUE          | empresa        |
| historico_atualizacoes  | PK              | id             |

### Indices ausentes recomendados

| Tabela                  | Coluna(s)             | Justificativa |
|-------------------------|-----------------------|---------------|
| inadimplentes           | empresa               | Todas as queries filtram por empresa — full scan sem indice |
| inadimplentes           | categoria             | Selecao de inadimplentes por faixa de cobranca |
| inadimplentes           | status                | Filtros por status operacional |
| inadimplentes           | dias_atraso           | Ordenacao e faixa de atraso |
| templates               | empresa               | Queries WHERE empresa = ? frequentes |
| templates               | (empresa, ativo)      | Indice composto para get_templates — ln 275 |
| envios                  | (empresa, data_envio) | get_envios_hoje usa LIKE em data_envio — query de alto custo — ln 335 |
| envios                  | (cpf, empresa)        | Busca historico de envios por aluno |
| historico_atualizacoes  | empresa               | Queries filtradas por empresa |

---

## Notas de Schema

- **Datas como TEXT:** Todas as datas sao armazenadas como strings no formato DD/MM/YYYY ou DD/MM/YYYY HH:MM:SS. Isso impede ordenacao e filtro temporal nativos no SQLite e exige conversao na camada de aplicacao.
- **Valores monetarios como REAL:** A coluna `total` usa REAL (ponto flutuante), sujeito a erros de arredondamento. Para valores monetarios recomenda-se INTEGER em centavos ou TEXT com escala fixa.
- **Discriminador de empresa como TEXT livre:** Nao existe tabela `empresas` nem CHECK constraint — qualquer string pode ser inserida como empresa sem validacao no banco.
- **Migracoes inline:** Todo o versionamento do schema esta embutido na funcao init_db() via ALTER TABLE condicionais. Nao existe ferramenta formal de migracao (Alembic, Flyway, etc.).
