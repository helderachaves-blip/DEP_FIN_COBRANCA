# 📦 HANDOFF - TRANSIÇÃO PARA PRÓXIMA MÁQUINA

**Data:** 19/05/2026  
**Status:** Pronto para transferência  
**Checklist:** Siga este guia para garantir que tudo está pronto

---

## ✅ CHECKLIST: O QUE COPIAR

### 📁 Pasta Principal
```
[ ] Copiar pasta completa: C:\Users\User\Desktop\MAT-INE - INADIMPLENCIA - 2026\

Conteúdo esperado ao copiar:
├─ INDICE_DO_PROJETO.md
├─ RESUMO_EXECUTIVO_PROJETO.md ........... LEIA PRIMEIRO!
├─ RELATORIO_ANALISE_COMPLETA.md
├─ ANALISE_PROCESSO_ATUAL_VS_NOVO.md
├─ PLANO_DE_TRABALHO_DETALHADO.md
├─ COMO_EXECUTAR_ANALISE.md
├─ ANALISE_DADOS.py
├─ 00_DOCUMENTACAO/
├─ 01_FASE_DIAGNOSTICO/
├─ 02_FASE_DESIGN/
├─ 03_FASE_IMPLEMENTACAO/
├─ 04_VALIDACAO_DEPLOY/
├─ 05_RECURSOS/
└─ BASE DE DADOS/
   ├─ *.xlsx (originais)
   └─ *.csv (arquivos analisados)
```

### ✅ Verificação Pós-Cópia
```
[ ] A pasta "MAT-INE - INADIMPLENCIA - 2026" foi copiada completamente?
[ ] Todos os 7 arquivos .md estão presentes?
[ ] Todas as 6 subpastas (00_ a 05_) estão presentes?
[ ] Os 4 arquivos de dados (2 xlsx + 2 csv) estão em BASE DE DADOS/?
[ ] O arquivo ANALISE_DADOS.py foi copiado?
```

---

## 🚀 COMO COMEÇAR NA NOVA MÁQUINA

### Passo 1: Exploração Inicial (5 min)
```
1. Abra a pasta "MAT-INE - INADIMPLENCIA - 2026"
2. Leia o arquivo: INDICE_DO_PROJETO.md
3. Leia o arquivo: RESUMO_EXECUTIVO_PROJETO.md
```

### Passo 2: Entender o Contexto (10 min)
```
1. Abra: RELATORIO_ANALISE_COMPLETA.md
2. Revise a estrutura dos dados (14 campos)
3. Note as 600 faturas em risco (~R$ 95.000)
```

### Passo 3: Validação de Dados (5 min)
```
1. Vá para BASE DE DADOS/
2. Verifique se os 4 arquivos estão lá:
   - VENCIDOS - 19-05-2026.csv ✓
   - VENCIDOS - 19-05-2026.xlsx ✓
   - NAO PAGOS - VINCENDAS - 19-05-2026.csv ✓
   - NAO PAGOS - VINCENDAS - 19-05-2026.xlsx ✓
```

### Passo 4: Próximas Ações
```
[ ] Responder as 3 QUESTÕES PENDENTES (ver abaixo)
[ ] Validar estrutura com Claude
[ ] Começar implementação
```

---

## ❓ 3 QUESTÕES CRÍTICAS (PENDENTES)

**Você PRECISA responder essas 3 perguntas para continuar.**

### 1️⃣ DADOS DE CONTATO NO SYNAPTA

Quando você acessa um aluno no Synapta (https://portal.matriculaead.com.br/admin/):

**Pergunta:** Você consegue ver/acessar:
- Email do aluno?
- Telefone/WhatsApp?
- Status (ativo/inativo)?

**Onde encontra isso?** (Menu > Submenu > Campo específico)

**Responda:**
```
Email disponível?        Sim ( ) Não ( )  Onde? __________
Telefone disponível?     Sim ( ) Não ( )  Onde? __________
WhatsApp disponível?     Sim ( ) Não ( )  Onde? __________
Status disponível?       Sim ( ) Não ( )  Onde? __________
```

### 2️⃣ API DO SYNAPTA

**Pergunta:** O Synapta tem API pública disponível?

**Responda:**
```
Tem API documentada?               Sim ( ) Não ( )
Você tem credenciais de acesso?    Sim ( ) Não ( )
Quem contatar no fornecedor?       __________________
Link da documentação:              __________________
```

Se NÃO tem API:
```
[ ] Você autoriza web scraping (ler automaticamente)?
[ ] Qual é a frequência ideal? (6:00 AM, 12:00, 18:00?)
```

### 3️⃣ REGRAS DE NEGÓCIO

**Pergunta:** Para automação de parcelamento, qual é a política?

**Responda:**
```
Parcelamento máximo: _____ vezes (2x, 3x, 4x?)
Valor mínimo de parcela: R$ ________
Juros no parcelamento: ___% ou Sem juros ( )

Cliente consegue parcelar sozinho?    Sim ( ) Não ( )
Você precisa aprovar?                  Sim ( ) Não ( )
Há limite de desconto?                 Sim ( ) Não ( )  Qual? __%

Casos que precisam você:
[ ] Desconto maior que __%
[ ] Parcelamento em mais de 4x
[ ] Cliente com histórico de inadimplência
[ ] Outro: ___________________________
```

---

## 📊 RESUMO RÁPIDO

### O que foi feito:
✅ Estrutura de projeto criada  
✅ Documentação completa  
✅ Dados analisados (600 faturas, ~R$ 95k)  
✅ Arquitetura desenhada  
✅ Roadmap definido  

### O que falta:
⏳ Respostas às 3 questões pendentes  
⏳ Implementação da automação  
⏳ Criação do banco de dados  
⏳ Testes  
⏳ Deploy  

### Tempo esperado:
📅 Coleta de informações: 1 dia  
📅 Desenvolvimento: 2-3 semanas  
📅 Testes: 1 semana  
📅 Deploy: 1 dia  
**Total: ~1 mês para sistema 100% funcional**

---

## 🔐 SEGURANÇA E PRIVACIDADE

### Dados Sensíveis Presentes:
```
⚠️ CPF de alunos (nos arquivos CSV)
⚠️ Nomes completos
⚠️ Valores de dívidas
⚠️ Dados de contato

AÇÃO:
[ ] Manter a pasta com acesso restrito
[ ] Não compartilhar CSVs com pessoas não autorizadas
[ ] Remover dados sensíveis antes de testar em desenvolvimento
[ ] Usar dados fictícios em testes
```

---

## 🎯 ESTRUTURA DE MEMÓRIA PARA CLAUDE

### Claude, quando voltar com a pasta, lembre-se:

**CONTEXTO:**
- Empresa: Matricula EaD
- Responsável: EDILVO (gerente@ineprotec.com.br)
- Objetivo: Automatizar cobranças (2.5-4h/dia → 15 min/dia)

**DADOS:**
- 297 faturas VENCIDAS (total ~R$ 50k)
- 297 faturas VINCENDAS (total ~R$ 45k)
- 14 campos estruturados
- ~200-250 clientes únicos

**ESTRUTURA CRIADA:**
- 6 pastas de fases (00 a 05)
- 7 documentos principais
- Scripts de análise Python
- Base de dados CSV dos clientes

**PRÓXIMOS PASSOS:**
1. Validar 3 questões pendentes
2. Implementar extração de dados (Synapta API)
3. Criar workflows de automação
4. Testar fluxo completo
5. Deploy em produção

**QUESTÕES PENDENTES:**
1. Dados de contato no Synapta?
2. API disponível?
3. Regras de parcelamento?

---

## 📞 CONTATOS IMPORTANTES

**Synapta:**
- Portal: https://portal.matriculaead.com.br/admin/
- Sistema: Gerenciador de recebimentos
- Tipo de acesso: Manual (sem API confirmada ainda)

**Projeto:**
- Responsável: EDILVO
- Email: gerente@ineprotec.com.br
- Data início: 19/05/2026

---

## ✨ PRONTO PARA CONTINUAR!

Copie a pasta, responda as 3 questões, e estaremos prontos para começar a implementação na próxima máquina! 🚀

**Próximo arquivo para ler quando voltar:**
→ RESUMO_EXECUTIVO_PROJETO.md

---

**Versão:** 1.0  
**Data:** 19/05/2026  
**Status:** ✅ PRONTO PARA TRANSFERÊNCIA
