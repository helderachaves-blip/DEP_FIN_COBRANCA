# MEMORY — MAT-INE Inadimplência 2026

> Contexto permanente do projeto. Atualizar apenas quando algo estrutural mudar.
> Última atualização: 08/06/2026

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
| `config_email` | Config SMTP por empresa |
| `historico_atualizacoes` | Log de atualizações da base |

---

## Rotas Principais

| Rota | Descrição |
|------|-----------|
| `/` | Início — upload e consolidação |
| `/resultado` | Resultado da consolidação com filtros |
| `/envio-mensagens` | Wizard de envio (WhatsApp + E-mail) |
| `/base` | Base de inadimplentes persistida |
| `/configuracoes` | Templates, SMTP, Régua, Clientes, Zona de Risco |
| `/crm/gerar-planilha` | Gera XLSX de tagging Kommo |

---

## Arquivos Principais do Código

| Arquivo | Responsabilidade |
|---------|-----------------|
| `06_APP/app.py` | Rotas Flask, lógica de negócio |
| `06_APP/database.py` | SQLite — schema, queries, migrations |
| `06_APP/processing.py` | Consolidação, geração de TXT/XLSX/CRM |
| `06_APP/templates/layout.html` | Sidebar, topbar, CSS global (Bootstrap 5.3.3) |
| `06_APP/templates/index.html` | Upload + ações de consolidação |
| `06_APP/templates/resultado.html` | Tabela de resultado com filtros |
| `06_APP/templates/envio_mensagens.html` | Wizard de envio (WhatsApp + E-mail) |
| `06_APP/templates/base.html` | Base persistida com cards de filtro |
| `06_APP/templates/configuracoes.html` | Configurações gerais |

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
