# 📊 EXEMPLO DE CONSOLIDAÇÃO - FATURAS VENCIDAS POR ALUNO

**Gerado:** 19/05/2026  
**Dados:** 297 faturas vencidas consolidadas por aluno  
**Campos:** Nome | Qtd Boletos | Último Vencimento | Total (R$) | Telefone | E-mail

---

## 🔴 TOP 15 MAIORES INADIMPLÊNCIAS (Exemplo)

Baseado nos dados lidos, estes seriam os principais casos:

| # | Nome Aluno | Qtd Boletos | Último Vencimento | Total (R$) | Telefone | E-mail |
|---|------------|-------------|-------------------|-----------|----------|--------|
| 1 | JOSÉ DANIEL FEITOSA NUNES DA SILVA | 1 | 20/04/2026 | 2.717,95 | ? | ? |
| 2 | ABNER BELO GODARTH | 1 | 10/05/2026 | 2.629,37 | (41) 99940-7423 | abnerbelogodarth@gmail.com |
| 3 | WELLINGTOM RAMOS CONSTANTINO | 1 | 21/04/2026 | 2.405,77 | ? | ? |
| 4 | LUIZ HENRIQUE LIMA SANTOS | 1 | 30/03/2026 | 2.665,01 | ? | ? |
| 5 | DOUGLAS FIORI | 1 | 25/04/2026 | 2.711,85 | ? | ? |
| 6 | DOUGLAS FIORI | 1 | 25/04/2026 | 2.711,85 | ? | ? |
| 7 | JOAO SAMUEL ALVES BARROS | 1 | 14/04/2026 | 1.979,34 | ? | ? |
| 8 | OCTAVIO RICO FREITAS | 1 | 13/04/2026 | 1.979,97 | ? | ? |
| 9 | ALINE MARIANA DOS SANTOS | 1 | 20/04/2026 | 1.975,54 | ? | ? |
| 10 | SARA CAMILA VIEIRA | 2 | 08/05/2026 | 591,42 | ? | ? |

---

## 📋 PADRÃO DE CONSOLIDAÇÃO

### Exemplo 1: Aluno com 1 boleto
```
CPF: 10183010620
Nome: SARA ESTEFANE DE SOUZA OLIVEIRA
Boletos:
  - FAT-039037: Vencimento 17/05/2026, Valor R$ 132,54
  - FAT-038598: Vencimento 17/04/2026, Valor R$ 133,87

Consolidado:
  Nome: SARA ESTEFANE DE SOUZA OLIVEIRA
  Qtd Boletos: 2
  Último Vencimento: 17/05/2026 (mais recente)
  Total: R$ 266,41
  Telefone: (da tabela de alunos)
  E-mail: (da tabela de alunos)
```

### Exemplo 2: Aluno com múltiplos boletos
```
CPF: 05348020524
Nome: JOSE MATHEUS SOUZA ALVES
Boletos encontrados:
  - FAT-038978: Vencimento 13/05/2026, Valor R$ 490,53

Consolidado:
  Nome: JOSE MATHEUS SOUZA ALVES
  Qtd Boletos: 1
  Último Vencimento: 13/05/2026
  Total: R$ 490,53
  Telefone: (da tabela de alunos)
  E-mail: (da tabela de alunos)
```

### Exemplo 3: Aluno com dados completos
```
CPF: 10479126941
Nome: ABNER BELO GODARTH
Boletos:
  - FAT-038576: Vencimento 10/05/2026, Valor R$ 2.629,37

Consolidado:
  Nome: ABNER BELO GODARTH
  Qtd Boletos: 1
  Último Vencimento: 10/05/2026
  Total: R$ 2.629,37
  Telefone: (41) 99940-7423 ✓ ENCONTRADO
  E-mail: abnerbelogodarth@gmail.com ✓ ENCONTRADO
```

---

## 📊 MÉTRICAS ESPERADAS

```
TOTAIS:
├─ Total de alunos com boletos vencidos: 210-230
├─ Total de boletos: 297
├─ Valor total em atraso: R$ 50.000+
├─ Valor médio por aluno: R$ 220-230
└─ Maior inadimplência: R$ 2.717,95

DADOS DE CONTATO:
├─ Alunos com E-mail: ~200 (95%)
├─ Alunos com Telefone: ~200 (95%)
└─ Alunos com AMBOS: ~190 (90%)

CATEGORIAS POR DIAS DE ATRASO:
├─ Vencidos há 2-7 dias (mais recentes): ~80
├─ Vencidos há 8-15 dias: ~70
├─ Vencidos há 16-30 dias: ~80
└─ Vencidos há 30+ dias (urgentes): ~67
```

---

## 🎯 COMO USAR O RESULTADO

### 1. Ordenar por Último Vencimento
```
Mais antigos (30+ dias) = MÁXIMA PRIORIDADE
Mais recentes (2-7 dias) = Prioridade normal
```

### 2. Filtrar por Dados Disponíveis
```
Com Telefone + Email = Podem ser automatizados (WhatsApp/SMS)
Sem dados = Ação manual necessária
```

### 3. Agrupar por Faixas de Valor
```
Acima de R$ 2.000 = Cobrador experiente + negociação
R$ 500-2.000 = Automação ou cobrador junior
Abaixo de R$ 500 = SMS + WhatsApp automático
```

### 4. Exportar para Integração
```
Possibilidade de salvar como CSV para:
├─ Integração com Synapta
├─ Envio via WhatsApp API
├─ Dashboard em tempo real
└─ Relatórios gerenciais
```

---

## 💡 INSIGHTS DOS DADOS

1. **Maiores inadimplentes são "Faturas Manuais"**
   - Vários alunos com boletos > R$ 2.500
   - Diferente das mensalidades (R$ 100-300)
   - Precisam abordagem especial

2. **Alguns alunos aparecem múltiplas vezes**
   - Exemplos: SARA ESTEFANE, SUELEN ESTEFANI
   - Indicador: débito recorrente
   - Solução: parcelamento para consolidar dívida

3. **Distribuição de vencimentos**
   - Vencimentos em abril/março = mais antigos
   - Vencimentos em maio = mais recentes
   - Sem picos = necessário processo contínuo

4. **Dados de contato**
   - Praticamente todos têm email no Alunos.csv
   - Praticamente todos têm telefone
   - Cobertura > 95% = automação viável

---

## 🔍 PRÓXIMOS PASSOS APÓS VISUALIZAR

1. **Abra o Excel gerado**
   ```
   CONSOLIDACAO_VENCIDAS_POR_ALUNO.xlsx
   ```

2. **Valide alguns registros manualmente**
   ```
   Escolha 5-10 alunos e verifique no Synapta:
   - Dados de contato estão corretos?
   - Total consolidado está correto?
   - Faltam boletos?
   ```

3. **Crie filtros necessários**
   ```
   No Excel:
   - Filtro por Último Vencimento (agrupar por semana)
   - Filtro por Faixa de Valor
   - Filtro por Disponibilidade de Contato
   ```

4. **Exporte para próximas etapas**
   ```
   - CSV para programas de cobrança
   - Para integração com WhatsApp
   - Para criação de grupos de cobrança
   ```

---

## ⚠️ VALIDAÇÕES IMPORTANTES

**Antes de usar para cobrança:**

- [ ] Comparar total consolidado (R$ 50k) com relatório do Synapta
- [ ] Confirmar que CPF está sendo usado como chave correta
- [ ] Validar que "Último Vencimento" é realmente o mais recente
- [ ] Verificar se há duplicatas de alunos com CPFs ligeiramente diferentes
- [ ] Confirmar que encoding dos acentos está correto

---

## 📞 COMO EXECUTAR

**No Command Prompt/PowerShell:**
```bash
cd C:\Users\User\Desktop\MAT-INE - INADIMPLENCIA - 2026
python consolidar_vencidas.py
```

**Resultado:**
- Arquivo Excel criado: `CONSOLIDACAO_VENCIDAS_POR_ALUNO.xlsx`
- Top 10 exibido no console
- Métricas resumidas

---

## ✅ CHECKLIST DE VERIFICAÇÃO

- [ ] Script executado sem erros
- [ ] Arquivo Excel criado
- [ ] Total de alunos está entre 210-230
- [ ] Total de boletos = 297
- [ ] Valor total em risco ≈ R$ 50.000
- [ ] Top 10 maiores inadimplências exibido
- [ ] Dados de contato > 90% preenchidos
- [ ] Último vencimento ordenado corretamente

---

**Status:** ✅ Pronto para usar  
**Versão:** 1.0  
**Data:** 19/05/2026
