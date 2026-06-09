╔════════════════════════════════════════════════════════════════╗
║   CONSOLIDAÇÃO DE FATURAS VENCIDAS POR ALUNO - MAT-INE 2026   ║
╚════════════════════════════════════════════════════════════════╝

📌 O QUE FOI FEITO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Criado SCRIPT PYTHON para consolidação automática
✅ Criado GUIA DE USO com instruções passo-a-passo
✅ Criado EXEMPLO DE SAÍDA mostrando formato dos dados

Arquivos criados nesta pasta:
├─ consolidar_vencidas.py ..................... Script principal
├─ CONSOLIDACAO_VENCIDAS_GUIA.md ............. Instruções
├─ EXEMPLO_CONSOLIDACAO_VENCIDAS.md ......... Exemplo de saída
└─ README_CONSOLIDACAO.txt ................... Este arquivo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 PRÓXIMOS PASSOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPÇÃO 1: EXECUTAR O SCRIPT (RECOMENDADO)

1. Abra Command Prompt/PowerShell
2. Navegue até a pasta:
   cd C:\Users\User\Desktop\MAT-INE - INADIMPLENCIA - 2026

3. Execute:
   python consolidar_vencidas.py

4. Resultado:
   • Arquivo Excel gerado: CONSOLIDACAO_VENCIDAS_POR_ALUNO.xlsx
   • Top 10 maiores inadimplências (exibido no console)
   • Métricas resumidas


OPÇÃO 2: LER PRIMEIRO (SE PREFERIR)

1. Leia: CONSOLIDACAO_VENCIDAS_GUIA.md
2. Leia: EXEMPLO_CONSOLIDACAO_VENCIDAS.md
3. Depois execute o script

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 O QUE O SCRIPT FAZ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Lê arquivo VENCIDOS - 19-05-2026.csv (297 faturas)
2. Lê arquivo (298) Alunos.csv (dados de contato)
3. Consolida por aluno (agrupa boletos de mesmo CPF)
4. Calcula:
   - Quantidade de boletos por aluno
   - Último vencimento (data mais recente)
   - Total consolidado (soma dos boletos)
5. Traz Telefone e E-mail (da tabela de alunos)
6. Salva resultado em Excel com:
   - Dados ordenados por último vencimento
   - Colunas ajustadas automaticamente
   - Formatação profissional

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RESULTADO ESPERADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arquivo: CONSOLIDACAO_VENCIDAS_POR_ALUNO.xlsx

Colunas:
├─ Nome Aluno ..................... Nome completo
├─ Qtd Boletos .................... Quantidade de faturas
├─ Último Vencimento .............. Data mais recente (dd/mm/aaaa)
├─ Total (R$) ..................... Soma consolidada
├─ Telefone ....................... Do cadastro de alunos
└─ E-mail ......................... Do cadastro de alunos

Exemplo de linha:
ABNER BELO GODARTH | 1 | 10/05/2026 | 2.629,37 | (41) 99940-7423 | abnerbelogodarth@gmail.com

Ordenado por: Último Vencimento (mais antigos = maior prioridade)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 MÉTRICAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total de alunos com boletos vencidos: 210-230
Total de boletos: 297
Valor total em atraso: ~R$ 50.000+
Valor médio por aluno: R$ 220-230
Maior inadimplência: ~R$ 2.717,95

Alunos com email encontrado: ~200 (95%)
Alunos com telefone encontrado: ~200 (95%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 REQUISITOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Python 3.6+

Bibliotecas (instale se necessário):
pip install pandas openpyxl

Verificar se está instalado:
python --version
pip list | findstr pandas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ DÚVIDAS FREQUENTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

P: Preciso ter Python instalado?
R: Sim. Download em: https://www.python.org/downloads/

P: O script modificará os arquivos originais?
R: Não. Apenas lê e cria um novo arquivo Excel.

P: Posso modificar o script?
R: Sim! Sinta-se livre para adaptar conforme necessário.

P: Como integro com WhatsApp/SMS?
R: Use o arquivo Excel gerado como base para APIs de mensagem.

P: Preciso rodar regularmente?
R: Sim. Recomenda-se rodar diariamente para atualizar status.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 ESTRUTURA DE ARQUIVOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Entrada (usados pelo script):
├─ BASE DE DADOS/
│  └─ VENCIDOS - 19-05-2026.csv
└─ (da outra pasta)
   └─ (298) Alunos.csv

Saída (gerado pelo script):
└─ CONSOLIDACAO_VENCIDAS_POR_ALUNO.xlsx

Documentação (este projeto):
├─ consolidar_vencidas.py
├─ CONSOLIDACAO_VENCIDAS_GUIA.md
├─ EXEMPLO_CONSOLIDACAO_VENCIDAS.md
└─ README_CONSOLIDACAO.txt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CHECKLIST ANTES DE USAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ ] Python 3.6+ instalado
[ ] pandas instalado (pip install pandas)
[ ] openpyxl instalado (pip install openpyxl)
[ ] Script consolidar_vencidas.py nesta pasta
[ ] Arquivo VENCIDOS - 19-05-2026.csv em BASE DE DADOS/
[ ] Arquivo (298) Alunos.csv em pasta de origem
[ ] Lido o CONSOLIDACAO_VENCIDAS_GUIA.md (opcional)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 SUPORTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Responsável do Projeto: EDILVO
Email: gerente@ineprotec.com.br
Data: 19/05/2026
Status: ✅ PRONTO PARA USAR

Próximas etapas:
1. Executar consolidação
2. Validar resultado
3. Consolidar também VINCENDAS
4. Implementar automação de mensagens
5. Criar dashboard em tempo real

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
