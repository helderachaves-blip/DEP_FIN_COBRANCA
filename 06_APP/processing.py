"""
Lógica de processamento pandas — extraída do app desktop.
Sem dependências de tkinter.
"""

import io
import re
import pandas as pd
from datetime import datetime
from pathlib import Path

# Uma "fonte" de leitura pode ser um Path em disco (uso local/testes) OU os bytes
# de um upload já em memória — `(BytesIO, filename)` — para o fluxo stateless da
# nuvem (EPIC-02 Onda 4), onde nada é gravado no filesystem.
Fonte = "Path | tuple[io.BytesIO, str]"


def _fonte_nome(fonte) -> str:
    """Nome legível da fonte (para mensagens de erro), seja Path ou (buffer, nome)."""
    return fonte[1] if isinstance(fonte, tuple) else fonte.name


class _SafeFormat(dict):
    """Mantém placeholders desconhecidos intactos, ex: {LINK_PAGAMENTO}."""
    def __missing__(self, key):
        return '{' + key + '}'


def fmt_brl(val: float) -> str:
    """Formata valor no padrão brasileiro: R$ 1.957,81"""
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def detectar_tratamento(nome: str) -> str:
    primeiro = nome.split()[0].lower()
    excecoes_masculinas = {'luca', 'joshua', 'nikita', 'danila', 'elisha'}
    if primeiro in excecoes_masculinas:
        return 'Sr.'
    excecoes_femininas = {'rachel', 'isabel', 'raquel', 'miriam', 'deborah', 'ruth', 'naomi', 'ester', 'noemi'}
    if primeiro in excecoes_femininas:
        return 'Sra.'
    return 'Sra.' if primeiro.endswith('a') else 'Sr.'


def _converter_valor(val) -> float:
    if val is None or val == '':
        return 0.0
    val_str = str(val).strip().replace('R$', '').strip()
    if ',' in val_str:
        val_str = val_str.replace('.', '').replace(',', '.')
    elif val_str.count('.') > 1:
        val_str = val_str.replace('.', '', val_str.count('.') - 1)
    try:
        return float(val_str)
    except Exception:
        return 0.0


def _ler_csv(fonte, coluna_obrigatoria: str) -> pd.DataFrame | None:
    """Lê CSV/XLSX de uma fonte (Path em disco OU `(BytesIO, filename)` em memória).

    Testa múltiplos encodings/separadores/skiprows (Synapta é inconsistente). Quando a
    fonte é um buffer em memória, faz `seek(0)` antes de cada tentativa para reaproveitar
    os mesmos bytes — nada é gravado em disco (EPIC-02 Onda 4, app stateless)."""
    if isinstance(fonte, tuple):
        buf, nome = fonte
        suffix = Path(nome).suffix.lower()

        def _src():
            buf.seek(0)
            return buf
    else:
        suffix = fonte.suffix.lower()

        def _src():
            return str(fonte)

    # Excel
    if suffix in ('.xlsx', '.xls'):
        for skip in [0, 1]:
            try:
                df = pd.read_excel(_src(), skiprows=skip or None)
                if coluna_obrigatoria in df.columns:
                    return df
            except Exception:
                pass
        return None
    # CSV
    for enc in ['utf-8', 'latin1', 'cp1252']:
        for sep in [',', ';', '\t']:
            for skip in [0, 1]:
                try:
                    df = pd.read_csv(_src(), encoding=enc, sep=sep, skiprows=skip)
                    if coluna_obrigatoria in df.columns:
                        return df
                except Exception:
                    pass
    return None


def consolidar(path_vencidos: Path, path_alunos: Path) -> tuple[pd.DataFrame, dict]:
    """
    Consolida vencidos + alunos e retorna (DataFrame consolidado, stats).
    Lança ValueError com mensagem legível em caso de problema.
    """
    vencidos = _ler_csv(path_vencidos, 'Aluno')
    if vencidos is None:
        raise ValueError(
            f"Não consegui ler '{_fonte_nome(path_vencidos)}'. "
            "Verifique se é o arquivo de Faturas Vencidas exportado do Synapta."
        )

    alunos = _ler_csv(path_alunos, 'CPF')
    if alunos is None:
        raise ValueError(
            f"Não consegui ler '{_fonte_nome(path_alunos)}'. "
            "Verifique se é o arquivo de Cadastro de Clientes."
        )

    vencidos['Aluno'] = vencidos['Aluno'].str.strip()
    vencidos['CPF sem mask'] = (
        vencidos['CPF sem mask'].astype(str).str.strip().str.zfill(11)
    )
    vencidos['Vencimento'] = pd.to_datetime(vencidos['Vencimento'], format='%d/%m/%Y')
    vencidos['Total'] = vencidos['Total'].apply(_converter_valor)

    consolidado = vencidos.groupby('CPF sem mask').agg({
        'Aluno':    'first',
        'Fatura #': 'count',
        'Vencimento': 'max',
        'Total':    'sum',
    }).reset_index()
    consolidado.columns = ['CPF', 'Aluno', 'Qtd_Boletos', 'Ultimo_Vencimento', 'Total']

    alunos['CPF_sem_mask'] = (
        alunos['CPF']
        .str.replace('.', '', regex=False)
        .str.replace('-', '', regex=False)
        .str.strip()
        .str.zfill(11)
    )
    alunos_dedup = (
        alunos[['CPF_sem_mask', 'E-mail', 'Telefone']]
        .drop_duplicates(subset=['CPF_sem_mask'])
    )
    consolidado = consolidado.merge(
        alunos_dedup, left_on='CPF', right_on='CPF_sem_mask', how='left',
    )

    # Alunos nos vencidos sem match no cadastro
    sem_cadastro_df = consolidado[consolidado['CPF_sem_mask'].isna()][['CPF', 'Aluno']]

    hoje = pd.Timestamp.now()
    consolidado['Dias_Atraso'] = (hoje - consolidado['Ultimo_Vencimento']).dt.days

    def classificar(row):
        if row['Dias_Atraso'] == 1:
            return 'Novos Inadimplentes'
        if row['Dias_Atraso'] <= 29:
            return 'Inadimplentes Mês'
        return 'Acima 30 Dias'

    consolidado['Categoria'] = consolidado.apply(classificar, axis=1)
    consolidado = consolidado.sort_values('Ultimo_Vencimento').reset_index(drop=True)

    total_novos   = int((consolidado['Categoria'] == 'Novos Inadimplentes').sum())
    total_mes     = int((consolidado['Categoria'] == 'Inadimplentes Mês').sum())
    total_acima30 = int((consolidado['Categoria'] == 'Acima 30 Dias').sum())
    stats = {
        'total': len(consolidado),
        'cat_novos':   total_novos,
        'cat_mes':     total_mes,
        'cat_acima30': total_acima30,
        'valor_total': float(consolidado['Total'].sum()),
        'valor_medio': float(consolidado['Total'].mean()),
        'com_telefone': int(consolidado['Telefone'].notna().sum()),
        'com_email': int(consolidado['E-mail'].notna().sum()),
        'sem_cadastro': len(sem_cadastro_df),
        'sem_cadastro_nomes': sem_cadastro_df['Aluno'].tolist(),
    }
    return consolidado, stats


def _slugify(titulo: str) -> str:
    s = titulo.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s-]+', '_', s)
    return s[:40]


def gerar_txt_template(titulo: str, template: str, dados: pd.DataFrame,
                       data_str: str, pasta: Path) -> Path:
    """Gera TXT de mensagens WhatsApp para qualquer template com intervalos de dias."""
    slug = _slugify(titulo)
    linhas = [
        "=" * 70,
        f"RELATÓRIO — {titulo.upper()}",
        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Total: {len(dados)} clientes",
        "=" * 70,
    ]
    for _, row in dados.iterrows():
        nome          = row['Aluno']
        telefone      = row['Telefone'] if pd.notna(row.get('Telefone')) else "N/A"
        venc          = (row['Ultimo_Vencimento'].strftime('%d/%m/%Y')
                         if hasattr(row['Ultimo_Vencimento'], 'strftime')
                         else str(row['Ultimo_Vencimento']))
        dias_atraso   = int(row['Dias_Atraso'])
        primeiro_nome = nome.split()[0].capitalize()
        tratamento    = detectar_tratamento(nome)
        mensagem = template.format_map(_SafeFormat(
            TRATAMENTO=tratamento, NOME=primeiro_nome, DATA_VENCIMENTO=venc,
        ))
        linhas += [
            f"\nCliente: {nome}",
            f"Telefone: {telefone}",
            f"Dias de Atraso: {dias_atraso}",
            f"Valor: {fmt_brl(row['Total'])}",
            "\nMensagem:",
            mensagem,
            "-" * 70,
        ]
    linhas += ["\n" + "=" * 70, "FIM DO RELATÓRIO", "=" * 70]
    arquivo = pasta / f"relatorio_{slug}_{data_str}.txt"
    arquivo.write_text('\n'.join(linhas), encoding='utf-8')
    return arquivo


def gerar_xlsx_template(titulo: str, dados: pd.DataFrame,
                        data_str: str, pasta: Path) -> Path:
    """Gera XLSX de relatório para qualquer template."""
    slug = _slugify(titulo)
    cols = [c for c in ['Aluno', 'Telefone', 'E-mail', 'Qtd_Boletos',
                         'Total', 'Ultimo_Vencimento', 'Dias_Atraso', 'Categoria']
            if c in dados.columns]
    df_export = dados[cols].copy()
    df_export.rename(columns={
        'Aluno': 'Nome Cliente', 'Qtd_Boletos': 'Qtd Títulos',
        'Total': 'Valor Total', 'Ultimo_Vencimento': 'Último Vencimento',
        'Dias_Atraso': 'Dias de Atraso',
    }, inplace=True)
    if 'Último Vencimento' in df_export.columns:
        df_export['Último Vencimento'] = df_export['Último Vencimento'].dt.strftime('%d/%m/%Y')
    if 'Valor Total' in df_export.columns:
        df_export['Valor Total'] = df_export['Valor Total'].apply(fmt_brl)
    arquivo = pasta / f"relatorio_{slug}_{data_str}.xlsx"
    df_export.to_excel(arquivo, index=False, sheet_name='Relatório')
    return arquivo


def gerar_txt(categoria: str, dados: pd.DataFrame, data_str: str,
              pasta: Path, template_novos: str, template_regua: str, template_acima30: str) -> Path:
    if categoria == 'Novos Inadimplentes':
        titulo     = "NOVOS INADIMPLENTES — COLOCAR TAG NO CRM"
        frequencia = "Enviar IMEDIATAMENTE — Adicionar tag INADIMPLENTE no CRM"
        template   = template_novos
        slug       = 'novos'
    elif categoria == 'Inadimplentes Mês':
        titulo     = "VENCIDOS — 2 A 29 DIAS"
        frequencia = "Enviar DIARIAMENTE"
        template   = template_regua
        slug       = 'mes'
    else:
        titulo     = "COBRANÇAS AVANÇADAS — ACIMA DE 30 DIAS"
        frequencia = "Enviar 1X POR SEMANA"
        template   = template_acima30
        slug       = 'acima30'

    linhas = [
        "=" * 70,
        f"RELATÓRIO DE MENSAGENS — {titulo}",
        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Frequência: {frequencia}",
        f"Total: {len(dados)} clientes",
        "=" * 70,
    ]

    for _, row in dados.iterrows():
        nome          = row['Aluno']
        telefone      = row['Telefone'] if pd.notna(row['Telefone']) else "N/A"
        vencimento    = row['Ultimo_Vencimento'].strftime('%d/%m/%Y')
        dias_atraso   = int(row['Dias_Atraso'])
        primeiro_nome = nome.split()[0].capitalize()
        tratamento    = detectar_tratamento(nome)

        mensagem = template.format_map(_SafeFormat(
            TRATAMENTO=tratamento,
            NOME=primeiro_nome,
            DATA_VENCIMENTO=vencimento,
        ))

        linhas += [
            f"\nCliente: {nome}",
            f"Telefone: {telefone}",
            f"Dias de Atraso: {dias_atraso}",
            f"Valor: {fmt_brl(row['Total'])}",
            "\nMensagem:",
            mensagem,
            "-" * 70,
        ]

    linhas += ["\n" + "=" * 70, "FIM DO RELATÓRIO", "=" * 70]

    arquivo = pasta / f"relatorio_{slug}_{data_str}.txt"
    arquivo.write_text('\n'.join(linhas), encoding='utf-8')
    return arquivo


def gerar_xlsx(categoria: str, dados: pd.DataFrame, data_str: str, pasta: Path) -> Path:
    df_export = dados[[
        'Aluno', 'Telefone', 'E-mail', 'Qtd_Boletos',
        'Total', 'Ultimo_Vencimento', 'Dias_Atraso', 'Categoria'
    ]].copy()
    df_export.columns = [
        'Nome Cliente', 'Telefone', 'E-mail', 'Qtd Títulos',
        'Valor Total', 'Último Vencimento', 'Dias de Atraso', 'Categoria'
    ]
    df_export['Último Vencimento'] = df_export['Último Vencimento'].dt.strftime('%d/%m/%Y')
    df_export['Valor Total'] = df_export['Valor Total'].apply(fmt_brl)

    if categoria == 'Novos Inadimplentes':
        slug = 'novos'
    elif categoria == 'Inadimplentes Mês':
        slug = 'mes'
    else:
        slug = 'acima30'
    arquivo = pasta / f"relatorio_{slug}_{data_str}.xlsx"
    df_export.to_excel(arquivo, index=False, sheet_name='Relatório')
    return arquivo


def gerar_relatorio_novos(dados: pd.DataFrame, data_str: str, pasta: Path) -> tuple[Path, Path]:
    linhas = [
        "=" * 70,
        "NOVOS INADIMPLENTES — ADICIONAR TAG NO CRM",
        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Total: {len(dados)} clientes",
        "Ação: Acrescentar tag INADIMPLENTE no cadastro do CRM",
        "=" * 70,
    ]
    for _, row in dados.iterrows():
        telefone = row['Telefone'] if pd.notna(row.get('Telefone')) else "N/A"
        email    = row['E-mail']   if pd.notna(row.get('E-mail'))   else "N/A"
        venc     = (row['Ultimo_Vencimento'].strftime('%d/%m/%Y')
                    if hasattr(row['Ultimo_Vencimento'], 'strftime')
                    else str(row['Ultimo_Vencimento']))
        linhas += [
            f"\nCliente:    {row['Aluno']}",
            f"CPF:        {row['CPF']}",
            f"Telefone:   {telefone}",
            f"E-mail:     {email}",
            f"Qtd Títulos:{int(row['Qtd_Boletos'])}",
            f"Valor:      {fmt_brl(row['Total'])}",
            f"Últ. Venc.: {venc}",
            "-" * 70,
        ]
    linhas += ["\n" + "=" * 70, "FIM DO RELATÓRIO", "=" * 70]

    arq_txt = pasta / f"NOVOS_INADIMPLENTES_{data_str}.txt"
    arq_txt.write_text('\n'.join(linhas), encoding='utf-8')

    df = dados[['CPF', 'Aluno', 'Telefone', 'E-mail',
                'Qtd_Boletos', 'Total', 'Ultimo_Vencimento', 'Categoria']].copy()
    df.columns = ['CPF', 'Nome Cliente', 'Telefone', 'E-mail',
                  'Qtd Títulos', 'Valor Total', 'Último Vencimento', 'Categoria']
    if len(df) > 0 and hasattr(df['Último Vencimento'].iloc[0], 'strftime'):
        df['Último Vencimento'] = df['Último Vencimento'].dt.strftime('%d/%m/%Y')
    df['Valor Total'] = df['Valor Total'].apply(fmt_brl)
    df['Ação CRM'] = 'ADICIONAR TAG INADIMPLENTE'

    arq_xlsx = pasta / f"NOVOS_INADIMPLENTES_{data_str}.xlsx"
    df.to_excel(arq_xlsx, index=False, sheet_name='Novos Inadimplentes')
    return arq_txt, arq_xlsx


def consolidar_avencer(path_avencer: Path, path_alunos: Path,
                       dias_antecedencia: int = 3) -> tuple[pd.DataFrame, dict]:
    """
    Processa arquivo A Vencer — retorna boletos vencendo dentro de `dias_antecedencia`.
    Suporta dois formatos Synapta:
      - Com 'CPF sem mask': merge por CPF (mais preciso)
      - Sem CPF: agrupa por Aluno e tenta merge por nome
    """
    avencer = _ler_csv(path_avencer, 'Aluno')
    if avencer is None:
        raise ValueError(
            f"Não consegui ler '{_fonte_nome(path_avencer)}'. "
            "Verifique se é o arquivo de Faturas a Vencer exportado do Synapta."
        )

    avencer['Aluno'] = avencer['Aluno'].str.strip()
    avencer['Vencimento'] = pd.to_datetime(avencer['Vencimento'], format='%d/%m/%Y')

    # Detecta coluna de valor
    col_valor = next(
        (c for c in ['Valor em aberto', 'Valor total', 'Total', 'Valor']
         if c in avencer.columns),
        None
    )
    if col_valor is None:
        raise ValueError(f"Coluna de valor não encontrada em '{_fonte_nome(path_avencer)}'.")
    avencer['_Valor'] = avencer[col_valor].apply(_converter_valor)

    # Detecta coluna de CPF
    col_cpf = next(
        (c for c in ['CPF sem mask', 'CPF'] if c in avencer.columns),
        None
    )

    hoje = pd.Timestamp.now().normalize()
    avencer['Dias_Para_Vencer'] = (avencer['Vencimento'] - hoje).dt.days

    # Filtra: boletos vencendo dentro do prazo
    lembrete_rows = avencer[avencer['Dias_Para_Vencer'].between(0, dias_antecedencia)].copy()

    if lembrete_rows.empty:
        return pd.DataFrame(), {'total': 0, 'com_telefone': 0}

    if col_cpf:
        # Formato com CPF (merge preciso)
        lembrete_rows[col_cpf] = lembrete_rows[col_cpf].astype(str).str.strip().str.zfill(11)
        consolidado = lembrete_rows.groupby(col_cpf).agg({
            'Aluno':      'first',
            'Vencimento': 'min',
            '_Valor':     'sum',
        }).reset_index()
        consolidado['Qtd_Boletos'] = lembrete_rows.groupby(col_cpf).size().values
        consolidado.columns = ['CPF', 'Aluno', 'Proximo_Vencimento', 'Total', 'Qtd_Boletos']

        alunos_df = _ler_csv(path_alunos, 'CPF')
        if alunos_df is not None:
            alunos_df['CPF_sem_mask'] = (
                alunos_df['CPF']
                .str.replace('.', '', regex=False)
                .str.replace('-', '', regex=False)
                .str.strip().str.zfill(11)
            )
            alunos_dedup = (
                alunos_df[['CPF_sem_mask', 'E-mail', 'Telefone']]
                .drop_duplicates(subset=['CPF_sem_mask'])
            )
            consolidado = consolidado.merge(
                alunos_dedup, left_on='CPF', right_on='CPF_sem_mask', how='left'
            )
        else:
            consolidado['Telefone'] = None
            consolidado['E-mail']   = None
    else:
        # Formato sem CPF (agrupa por nome)
        consolidado = lembrete_rows.groupby('Aluno').agg({
            'Vencimento': 'min',
            '_Valor':     'sum',
        }).reset_index()
        consolidado['Qtd_Boletos'] = lembrete_rows.groupby('Aluno').size().values
        consolidado.rename(columns={'Vencimento': 'Proximo_Vencimento', '_Valor': 'Total'}, inplace=True)
        consolidado['CPF'] = ''

        # Tenta merge por nome com alunos
        alunos_df = _ler_csv(path_alunos, 'CPF')
        if alunos_df is not None:
            nome_col = next((c for c in ['Aluno', 'Nome', 'nome'] if c in alunos_df.columns), None)
            if nome_col:
                alunos_df['_nome_norm'] = alunos_df[nome_col].str.strip().str.upper()
                consolidado['_nome_norm'] = consolidado['Aluno'].str.strip().str.upper()
                alunos_dedup = (
                    alunos_df[['_nome_norm', 'E-mail', 'Telefone', 'CPF']]
                    .drop_duplicates(subset=['_nome_norm'])
                )
                consolidado = consolidado.merge(alunos_dedup, on='_nome_norm', how='left')
                consolidado['CPF'] = (
                    consolidado['CPF_y'].fillna('') if 'CPF_y' in consolidado.columns
                    else consolidado.get('CPF', '')
                )
                consolidado.drop(columns=['_nome_norm', 'CPF_y', 'CPF_x'],
                                 errors='ignore', inplace=True)
            else:
                consolidado['Telefone'] = None
                consolidado['E-mail']   = None
        else:
            consolidado['Telefone'] = None
            consolidado['E-mail']   = None

    hoje_norm = pd.Timestamp.now().normalize()
    consolidado['Categoria'] = consolidado['Proximo_Vencimento'].apply(
        lambda v: 'Vence Hoje' if pd.Timestamp(v).normalize() == hoje_norm else 'A Vencer'
    )
    consolidado = consolidado.sort_values('Proximo_Vencimento').reset_index(drop=True)

    vence_hoje = int((consolidado['Categoria'] == 'Vence Hoje').sum())
    stats = {
        'total': len(consolidado),
        'vence_hoje': vence_hoje,
        'com_telefone': int(consolidado['Telefone'].notna().sum())
        if 'Telefone' in consolidado.columns else 0,
        'dias_antecedencia': dias_antecedencia,
    }
    return consolidado, stats


def gerar_txt_avencer(dados: pd.DataFrame, data_str: str, pasta: Path, template: str) -> Path:
    linhas = [
        "=" * 70,
        "LEMBRETES DE VENCIMENTO — BOLETOS VENCENDO HOJE / AMANHÃ",
        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "Frequência: Enviar HOJE — Boleto vence hoje ou amanhã",
        f"Total: {len(dados)} clientes",
        "=" * 70,
    ]

    for _, row in dados.iterrows():
        nome          = row['Aluno']
        telefone      = row['Telefone'] if pd.notna(row.get('Telefone', None)) else "N/A"
        vencimento    = row['Proximo_Vencimento'].strftime('%d/%m/%Y')
        primeiro_nome = nome.split()[0].capitalize()
        tratamento    = detectar_tratamento(nome)

        mensagem = template.format_map(_SafeFormat(
            TRATAMENTO=tratamento,
            NOME=primeiro_nome,
            DATA_VENCIMENTO=vencimento,
        ))

        linhas += [
            f"\nCliente: {nome}",
            f"Telefone: {telefone}",
            f"Vencimento: {vencimento}",
            f"Valor: {fmt_brl(row['Total'])}",
            "\nMensagem:",
            mensagem,
            "-" * 70,
        ]

    linhas += ["\n" + "=" * 70, "FIM DO RELATÓRIO", "=" * 70]

    arquivo = pasta / f"relatorio_avencer_{data_str}.txt"
    arquivo.write_text('\n'.join(linhas), encoding='utf-8')
    return arquivo


def gerar_xlsx_avencer(dados: pd.DataFrame, data_str: str, pasta: Path) -> Path:
    cols = [c for c in ['Aluno', 'Telefone', 'E-mail', 'Qtd_Boletos', 'Total', 'Proximo_Vencimento']
            if c in dados.columns]
    df_export = dados[cols].copy()
    df_export.columns = ['Nome Aluno', 'Telefone', 'E-mail', 'Qtd Títulos',
                          'Valor Total', 'Próximo Vencimento'][:len(cols)]
    if 'Próximo Vencimento' in df_export.columns:
        df_export['Próximo Vencimento'] = df_export['Próximo Vencimento'].dt.strftime('%d/%m/%Y')
    if 'Valor Total' in df_export.columns:
        df_export['Valor Total'] = df_export['Valor Total'].apply(fmt_brl)
    arquivo = pasta / f"relatorio_avencer_{data_str}.xlsx"
    df_export.to_excel(arquivo, index=False, sheet_name='A Vencer')
    return arquivo


def gerar_relatorio_saidos(dados: pd.DataFrame, data_str: str, pasta: Path) -> tuple[Path, Path]:
    linhas = [
        "=" * 70,
        "SAÍRAM DOS VENCIDOS — REVISAR: QUITADOS OU RENEGOCIADOS",
        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Total: {len(dados)} clientes",
        "ATENÇÃO: Verificar manualmente se cada cliente PAGOU ou RENEGOCIOU.",
        "  -> PAGOU:       Remover tag INADIMPLENTE no CRM",
        "  -> RENEGOCIOU:  Manter tag INADIMPLENTE no CRM",
        "=" * 70,
    ]
    for _, row in dados.iterrows():
        telefone = row.get('Telefone', 'N/A')
        telefone = telefone if pd.notna(telefone) else "N/A"
        email    = row.get('E-mail', 'N/A')
        email    = email if pd.notna(email) else "N/A"
        linhas += [
            f"\nCliente:  {row['Aluno']}",
            f"CPF:      {row['CPF']}",
            f"Telefone: {telefone}",
            f"E-mail:   {email}",
            f"Situacao: [ ] Pagou - remover tag   [ ] Renegociou - manter tag",
            "-" * 70,
        ]
    linhas += ["\n" + "=" * 70, "FIM DO RELATÓRIO", "=" * 70]

    arq_txt = pasta / f"SAIDOS_VENCIDOS_{data_str}.txt"
    arq_txt.write_text('\n'.join(linhas), encoding='utf-8')

    colunas = [c for c in ['CPF', 'Aluno', 'Telefone', 'E-mail', 'Data_Entrada', 'Categoria']
               if c in dados.columns]
    df = dados[colunas].copy()
    df['Situacao'] = ''
    df['Acao CRM'] = 'VERIFICAR — Pagou (remover tag) ou Renegociou (manter tag)'

    arq_xlsx = pasta / f"SAIDOS_VENCIDOS_{data_str}.xlsx"
    df.to_excel(arq_xlsx, index=False, sheet_name='Saíram dos Vencidos')
    return arq_txt, arq_xlsx


def _encontrar_template_crm(dias_atraso: int, templates: list) -> dict | None:
    candidatos = [
        t for t in templates
        if t.get('dias_de') is not None
        and t['dias_de'] >= 0
        and t['dias_de'] <= dias_atraso
        and (t.get('dias_ate') is None or t['dias_ate'] >= dias_atraso)
    ]
    return max(candidatos, key=lambda t: t['dias_de']) if candidatos else None


def obter_cpfs_avencer(path: Path) -> set:
    """
    Retorna TODOS os CPFs presentes no arquivo A Vencer, independente da data.
    Usado para detectar renegociação: se o aluno saiu dos vencidos mas tem fatura futura.
    """
    df = _ler_csv(path, 'Aluno')
    if df is None:
        return set()
    col_cpf = next((c for c in ['CPF sem mask', 'CPF'] if c in df.columns), None)
    if not col_cpf:
        return set()
    mask = df[col_cpf].astype(str).str.strip() != ''
    return set(df.loc[mask, col_cpf].astype(str).str.strip().str.zfill(11))


def processar_pagos_cancelados(path: Path) -> tuple[set, set]:
    """
    Lê o relatório de pagos/cancelados do Synapta.
    Retorna (cpfs_pagos, cpfs_cancelados).
    """
    df = _ler_csv(path, 'CPF sem mask')
    if df is None:
        raise ValueError(
            f"Não consegui ler '{_fonte_nome(path)}'. "
            "Verifique se é o relatório de Pagos e Cancelados exportado do Synapta."
        )
    df['CPF sem mask'] = df['CPF sem mask'].astype(str).str.strip().str.zfill(11)
    df['Status'] = df['Status'].astype(str).str.strip()
    cpfs_pagos      = set(df.loc[df['Status'] == 'Pago',      'CPF sem mask'])
    cpfs_cancelados = set(df.loc[df['Status'] == 'Cancelado', 'CPF sem mask'])
    return cpfs_pagos, cpfs_cancelados


def gerar_planilha_crm(consolidado: pd.DataFrame, base_df: pd.DataFrame,
                        templates_list: list, pasta: Path,
                        data_str: str, empresa: str) -> Path:
    """Planilha CRM com 2 abas: Inadimplentes (com tag) + Saídos/Quitados."""
    inad_rows = []
    for _, row in consolidado.iterrows():
        tmpl = _encontrar_template_crm(int(row['Dias_Atraso']), templates_list)
        tag  = (tmpl.get('tag_crm') or '') if tmpl else ''
        inad_rows.append({
            'Nome':        row['Aluno'],
            'CPF':         str(row['CPF']).zfill(11),
            'Telefone':    str(row.get('Telefone') or ''),
            'E-mail':      str(row.get('E-mail') or ''),
            'Categoria':   row['Categoria'],
            'Dias Atraso': int(row['Dias_Atraso']),
            'Valor (R$)':  float(row['Total']),
            'Tag CRM':     tag,
        })

    cpfs_consolidado = set(consolidado['CPF'].astype(str).str.zfill(11))
    saidos_rows = []
    if not base_df.empty:
        for _, row in base_df.iterrows():
            cpf = str(row['cpf'])
            if cpf not in cpfs_consolidado or row.get('status', '') in ('QUITADO', 'RENEGOCIADO'):
                saidos_rows.append({
                    'Nome':     row['aluno'],
                    'CPF':      cpf,
                    'Telefone': str(row.get('telefone') or ''),
                    'E-mail':   str(row.get('email') or ''),
                    'Status':   row.get('status', ''),
                    'Ação CRM': 'REMOVER_TAG',
                })

    df_inad   = pd.DataFrame(inad_rows)   if inad_rows   else pd.DataFrame()
    df_saidos = pd.DataFrame(saidos_rows) if saidos_rows else pd.DataFrame()

    nome_arq = pasta / f"CRM_{empresa}_{data_str}.xlsx"
    with pd.ExcelWriter(nome_arq, engine='openpyxl') as writer:
        df_inad.to_excel(writer,   sheet_name='Inadimplentes',    index=False)
        df_saidos.to_excel(writer, sheet_name='Saídos_Quitados',  index=False)

    return nome_arq
