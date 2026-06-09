# 📊 CONSOLIDAÇÃO DE FATURAS VENCIDAS POR ALUNO
## Guia de Uso e Script

**Data:** 19/05/2026  
**Objetivo:** Consolidar 297 faturas vencidas por aluno, agrupando quantidade de boletos, último vencimento, telefone e e-mail

---

## ✅ O QUE FAZER

### Opção 1: Usar o Script Python (RECOMENDADO)

Na pasta do projeto, você encontrará o arquivo:
```
consolidar_vencidas.py
```

**Como executar:**
```bash
python consolidar_vencidas.py
```

**O que o script faz:**
1. Lê o arquivo VENCIDOS - 19-05-2026.csv (297 faturas)
2. Lê o arquivo (298) Alunos.csv (dados de contato)
3. Consolida por CPF (agrupa boletos de cada aluno)
4. Calcula:
   - **Quantidade de boletos** por aluno
   - **Último vencimento** (data mais recente)
   - **Total consolidado** (soma de todos os boletos)
5. Traz **Telefone** e **E-mail** do arquivo de alunos
6. **Salva em Excel**: `CONSOLIDACAO_VENCIDAS_POR_ALUNO.xlsx`

**Saída do script:**
- ✓ Arquivo Excel com dados consolidados
- ✓ Top 10 maiores inadimplências (na console)
- ✓ Métricas (total de alunos, boletos, valores)

---

## 📋 ESTRUTURA DE DADOS

### Entrada 1: VENCIDOS - 19-05-2026.csv
```
Campos: Fatura #, Tipo, Origem, Ano, Data, Vencimento, Aluno, Subtotal, 
        Descontos, Multas e Juros, Total, Ações, Status, CPF, CPF sem mask

Total: 297 faturas
Valor total: ~R$ 50.000+
Exemplos:
- SARA ESTEFANE DE SOUZA OLIVEIRA (CPF: 10183010620) - R$ 132,54
- ABNER BELO GODARTH (CPF: 10479126941) - R$ 2.629,37
- WELLINGTOM RAMOS (CPF: 47837437896) - R$ 2.405,77
```

### Entrada 2: (298) Alunos.csv
```
Campos: #, Nome, Origem, CPF, E-mail, Telefone, Ativo, Data de Cadastro

Total: 298 alunos
Exemplo:
- AL-007112, ABNER BELO GODARTH, CPF: 104.791.269-41
  Email: abnerbelogodarth@gmail.com
  Telefone: (41) 99940-7423
```

### Saída: CONSOLIDACAO_VENCIDAS_POR_ALUNO.xlsx
```
Colunas: Nome Aluno | Qtd Boletos | Último Vencimento | Total (R$) | Telefone | E-mail | CPF

Exemplo de linha:
ABNER BELO GODARTH | 1 | 10/05/2026 | R$ 2.629,37 | (41) 99940-7423 | abnerbelogodarth@gmail.com | 104.791.269-41

Ordenado por: Último Vencimento (mais antigos primeiro = maior risco)
```

---

## 🎯 CASOS DE USO

### 1. Identificar maiores inadimplências
```
O script mostra TOP 10 automaticamente com:
- Nome do aluno
- Quantidade de boletos
- Valor total
- Contato (telefone e email)
```

### 2. Priorizar cobranças
```
Alunos com ÚLTIMO VENCIMENTO mais antigo = MAIOR PRIORIDADE
(vencimentos de abril/março precisam de ação imediata)
```

### 3. Validar dados de contato
```
Alunos com Telefone = NULL ou E-mail = NULL
Necessitam busca manual de dados no Synapta
```

### 4. Agrupar por "cobrável"
```
Alunos com dados completos (telefone + email) = podem ser automatizados
Alunos sem dados = ação manual necessária
```

---

## 📊 MÉTRICAS ESPERADAS

Após executar o script, você verá:

```
RESUMO:
  • Total de alunos com boletos vencidos: ~200-220
  • Total de boletos: 297
  • Valor total em atraso: ~R$ 50.000+
  • Valor médio por aluno: ~R$ 225-230
  • Maior inadimplência: ~R$ 2.717 (JOSÉ DANIEL FEITOSA)
  
  ✓ Alunos com email encontrado: ~180-200
  ✓ Alunos com telefone encontrado: ~180-200
```

---

## 🚀 PRÓXIMOS PASSOS APÓS CONSOLIDAÇÃO

1. **Abra o Excel gerado**
   - `CONSOLIDACAO_VENCIDAS_POR_ALUNO.xlsx`

2. **Filtre por "Último Vencimento"**
   - Maiores que 30 dias = ação urgente
   - 15-30 dias = cobrança moderada
   - < 15 dias = lembrete

3. **Use os dados para:**
   - Enviar WhatsApp (via automação)
   - Enviar SMS
   - Consultar Synapta para mais detalhes
   - Oferecer parcelamento

4. **Atualize conforme recebimentos:**
   - Roda o script novamente para gerar nova consolidação
   - Compara com anterior para validar recebimentos

---

## 🔧 REQUISITOS

**Python 3.6+**

**Bibliotecas necessárias:**
```bash
pip install pandas openpyxl
```

**Arquivos necessários (automaticamente detectados):**
- ✓ VENCIDOS - 19-05-2026.csv
- ✓ (298) Alunos.csv

---

## ❓ DÚVIDAS FREQUENTES

### P: O script não encontra os arquivos?
**R:** Verifique os paths no topo do script:
```python
vencidos_path = r"C:\Users\User\Desktop\MAT-INE - INADIMPLENCIA - 2026\BASE DE DADOS\..."
alunos_path = r"C:\Users\User\Desktop\INADIMPLÊNCIA MATRICULA EAD - 2026\00 - BASE DE DADOS\..."
```

### P: Alguns alunos não têm email/telefone?
**R:** Normal! Significa que:
- Dados não foram preenchidos no cadastro
- Podem estar em outra aba do Synapta
- Precisam busca manual

### P: Posso modificar o script?
**R:** Sim! Sugestões:
- Adicionar filtro por data (últimos 30 dias)
- Adicionar coluna de dias de atraso
- Exportar para CSV em vez de Excel
- Enviar relatório por email automaticamente

---

## 📞 CONTATO PARA DÚVIDAS

**Responsável do Projeto:** EDILVO  
**Email:** gerente@ineprotec.com.br  
**Sistema Synapta:** https://portal.matriculaead.com.br/admin/

---

## 📈 PRÓXIMA ETAPA

Após consolidação dos vencidos:

1. **Consolidar VINCENDAS** (com mesma estrutura)
2. **Criar matriz de ações** (por dias de atraso)
3. **Implementar automação** (WhatsApp, SMS, etc)
4. **Dashboard em tempo real**

---

**Status:** ✅ Pronto para executar  
**Versão:** 1.0  
**Data:** 19/05/2026
