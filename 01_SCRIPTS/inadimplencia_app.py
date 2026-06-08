#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APLICAÇÃO CONSOLIDADOR DE INADIMPLÊNCIAS
Matricula EaD - MAT-INE 2026

Autor: Helder (TI) + Claude
Data: 20/05/2026
Objetivo: Consolidar faturas vencidas e gerar relatórios para WhatsApp

Fase 1: Consolidação e Geração de Relatórios (sem integração Kommo)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
import os
import shutil
from pathlib import Path
from PIL import Image, ImageTk

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

PROJETO_DIR           = Path(__file__).parent.parent
BASE_DE_DADOS_DIR      = PROJETO_DIR / "BASE DE DADOS"
RELATORIOS_DIR        = PROJETO_DIR / "RELATORIOS"
LOGS_DIR              = PROJETO_DIR / "LOGS"
BASE_INADIMPLENTES    = BASE_DE_DADOS_DIR / "BASE_INADIMPLENTES.xlsx"
UTILITARIOS_DIR       = PROJETO_DIR / "UTILITARIOS"
LOGO_INEPROTEC        = UTILITARIOS_DIR / "Logo.png"
LOGO_MATRICULA        = UTILITARIOS_DIR / "Logo Matrícula Ead_.png"

LOGS_DIR.mkdir(exist_ok=True)

# Templates de mensagem
MENSAGEM_A = """Olá, {TRATAMENTO} {NOME}. Tudo bem?
Somos do setor financeiro do Matricula EaD.
Para sua maior comodidade estamos enviando o boleto referente ao seu Curso Técnico, com vencimento em {DATA_VENCIMENTO}.
Se já realizou o pagamento, favor desconsiderar a mensagem!
Qualquer dúvida estamos à disposição!"""

MENSAGEM_B = """Olá, {TRATAMENTO} {NOME}. Tudo bem?
Somos do setor financeiro do Matricula EaD. O motivo do meu contato é referente ás parcelas em aberto do seu Curso Técnico em Agropecuária. Tem interesse em retornar ao curso?"""


def detectar_tratamento(nome):
    """Detecta sr. ou sra. pelo primeiro nome (heurística para nomes brasileiros)."""
    primeiro = nome.split()[0].lower()
    excecoes_masculinas = {'luca', 'joshua', 'nikita', 'danila', 'elisha'}
    if primeiro in excecoes_masculinas:
        return 'sr.'
    excecoes_femininas = {'rachel', 'isabel', 'raquel', 'miriam', 'deborah', 'ruth', 'naomi', 'ester', 'noemi'}
    if primeiro in excecoes_femininas:
        return 'sra.'
    if primeiro.endswith('a'):
        return 'sra.'
    return 'sr.'


def get_pasta_data(base):
    """Retorna pasta com estrutura Ano/Mês/Dia, criando se necessário."""
    hoje = datetime.now()
    pasta = base / str(hoje.year) / f"{hoje.month:02d}" / f"{hoje.day:02d}"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


# ============================================================================
# CLASSE PRINCIPAL
# ============================================================================

class AplicacaoInadimplencia:
    def __init__(self, root):
        self.root = root
        self.root.title("Cobranças - Ineprotec / Matrícula EAD")
        self.root.geometry("960x820")
        self.root.resizable(True, True)

        # Manter referências para evitar garbage collection
        self._img_ineprotec = None
        self._img_matricula = None

        # Dados processados
        self.vencidos    = None
        self.alunos      = None
        self.consolidacao = None

        # Paths dos arquivos selecionados
        self.path_alunos  = self._detectar_arquivo_padrao('alunos')
        self.path_vencidos = self._detectar_arquivo_padrao('vencidos')
        self.path_avencer  = self._detectar_arquivo_padrao('avencer')

        self.criar_interface()
        self.log("Aplicação iniciada")

    # ------------------------------------------------------------------
    # DETECÇÃO AUTOMÁTICA DE ARQUIVOS PADRÃO
    # ------------------------------------------------------------------

    def _detectar_arquivo_padrao(self, tipo):
        """Procura o arquivo mais recente na pasta datada de hoje ou na raiz."""
        padroes = {
            'alunos':   ['*luno*', '*(298)*'],
            'vencidos': ['VENCIDOS_*', '*VENCIDO*', '*vencido*'],
            'avencer':  ['AVENCER_*', '*VINCENDA*', '*vincenda*'],
        }
        hoje = datetime.now()
        pasta_hoje = BASE_DE_DADOS_DIR / str(hoje.year) / f"{hoje.month:02d}" / f"{hoje.day:02d}"

        for pasta in [pasta_hoje, BASE_DE_DADOS_DIR]:
            if not pasta.exists():
                continue
            for padrao in padroes.get(tipo, []):
                encontrados = list(pasta.glob(padrao))
                if encontrados:
                    return encontrados[0]
        return None

    # ------------------------------------------------------------------
    # INTERFACE
    # ------------------------------------------------------------------

    def criar_interface(self):
        """Cria a interface gráfica."""

        # ===== HEADER =====
        header = tk.Frame(self.root, bg="#1a1a2e", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Logo Ineprotec — esquerda
        if LOGO_INEPROTEC.exists():
            img = Image.open(LOGO_INEPROTEC)
            img = img.resize((200, 50), Image.LANCZOS)
            self._img_ineprotec = ImageTk.PhotoImage(img)
            tk.Label(header, image=self._img_ineprotec, bg="#1a1a2e").pack(
                side=tk.LEFT, padx=16, pady=15)

        # Título centralizado
        tk.Label(
            header,
            text="Cobranças - Ineprotec / Matrícula EAD",
            font=("Arial", 15, "bold"),
            fg="white",
            bg="#1a1a2e",
        ).pack(side=tk.LEFT, expand=True)

        # Logo Matrícula EaD — direita
        if LOGO_MATRICULA.exists():
            img2 = Image.open(LOGO_MATRICULA)
            img2 = img2.resize((200, 50), Image.LANCZOS)
            self._img_matricula = ImageTk.PhotoImage(img2)
            tk.Label(header, image=self._img_matricula, bg="#1a1a2e").pack(
                side=tk.RIGHT, padx=16, pady=15)

        # ===== ARQUIVOS DE ENTRADA =====
        arquivos_frame = ttk.LabelFrame(self.root, text="Arquivos de Entrada", padding=8)
        arquivos_frame.pack(fill=tk.X, padx=10, pady=5)

        for tipo, texto, attr in [
            ('alunos',   '📂 Alunos',    'label_alunos'),
            ('vencidos', '📂 Vencidos',  'label_vencidos'),
            ('avencer',  '📂 À Vencer',  'label_avencer'),
        ]:
            linha = ttk.Frame(arquivos_frame)
            linha.pack(fill=tk.X, pady=2)

            path_atual = getattr(self, f'path_{tipo}')
            ttk.Button(linha, text=texto, width=14,
                       command=lambda t=tipo: self.selecionar_arquivo(t)).pack(side=tk.LEFT)
            label = ttk.Label(linha, text=self._texto_arquivo(path_atual), font=("Arial", 9))
            label.pack(side=tk.LEFT, padx=8)
            setattr(self, attr, label)

        # ===== STATUS =====
        status_frame = ttk.LabelFrame(self.root, text="Status", padding=8)
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_text = tk.Text(status_frame, height=3, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # ===== BOTÕES — LINHA 1 =====
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(8, 2))

        ttk.Button(buttons_frame, text="📥 Consolidar Vencidas",
                   command=self.consolidar_vencidas).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons_frame, text="📊 Visualizar Resultado",
                   command=self.visualizar_resultado).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons_frame, text="📄 Gerar Relatório WhatsApp",
                   command=self.gerar_relatorio).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons_frame, text="📁 Abrir Relatórios",
                   command=self.abrir_relatorios).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons_frame, text="🗑️ Limpar",
                   command=self.limpar).pack(side=tk.LEFT, padx=4)

        # ===== BOTÕES — LINHA 2 (Gestão de Base) =====
        base_frame = ttk.LabelFrame(self.root, text="Gestão de Base de Inadimplentes / Tag CRM", padding=6)
        base_frame.pack(fill=tk.X, padx=10, pady=(2, 6))

        ttk.Button(base_frame, text="🔄 Comparar e Atualizar Base",
                   command=self.comparar_e_atualizar_base).pack(side=tk.LEFT, padx=4)

        self.label_base_status = ttk.Label(base_frame, text=self._status_base(), font=("Arial", 9))
        self.label_base_status.pack(side=tk.LEFT, padx=12)

        # ===== TABELA =====
        tabela_frame = ttk.LabelFrame(self.root, text="Resultado da Consolidação", padding=10)
        tabela_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar_v = ttk.Scrollbar(tabela_frame, orient=tk.VERTICAL)
        scrollbar_h = ttk.Scrollbar(tabela_frame, orient=tk.HORIZONTAL)

        self.tabela = ttk.Treeview(
            tabela_frame,
            columns=("Nome", "Qtd", "Valor", "Categoria"),
            height=15,
            yscrollcommand=scrollbar_v.set,
            xscrollcommand=scrollbar_h.set,
        )
        self.tabela.column("#0",        width=0)
        self.tabela.column("Nome",      anchor="w",      width=350)
        self.tabela.column("Qtd",       anchor="center", width=80)
        self.tabela.column("Valor",     anchor="e",      width=120)
        self.tabela.column("Categoria", anchor="center", width=180)

        self.tabela.heading("Nome",      text="Nome do Aluno")
        self.tabela.heading("Qtd",       text="Qtd Títulos")
        self.tabela.heading("Valor",     text="Valor Total (R$)")
        self.tabela.heading("Categoria", text="Categoria")

        scrollbar_v.config(command=self.tabela.yview)
        scrollbar_h.config(command=self.tabela.xview)

        self.tabela.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)

        # ===== RODAPÉ =====
        footer = ttk.Frame(self.root)
        footer.pack(fill=tk.X, padx=10, pady=5)
        self.info_label = ttk.Label(footer, text="Pronto para consolidar", font=("Arial", 9))
        self.info_label.pack(side=tk.LEFT)

        self.log("Interface criada com sucesso")

    # ------------------------------------------------------------------
    # ARQUIVOS DE ENTRADA
    # ------------------------------------------------------------------

    def _texto_arquivo(self, path):
        """Texto exibido no label de um arquivo."""
        if path and Path(path).exists():
            return f"✅  {Path(path).name}"
        return "⚠️  Nenhum arquivo selecionado"

    def selecionar_arquivo(self, tipo):
        """Abre diálogo de seleção, renomeia conforme padrão e copia para pasta datada."""
        titulos = {
            'alunos':   "Selecionar arquivo de Cadastro de Alunos",
            'vencidos': "Selecionar arquivo de Faturas Vencidas",
            'avencer':  "Selecionar arquivo de Faturas À Vencer",
        }

        caminho = filedialog.askopenfilename(
            title=titulos[tipo],
            filetypes=[("CSV e Excel", "*.csv *.xlsx *.xls"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        extensao = Path(caminho).suffix
        data_str = datetime.now().strftime('%d-%m-%Y')

        # Nome padronizado por tipo
        nomes_padrao = {
            'vencidos': f"VENCIDOS_{data_str}{extensao}",
            'avencer':  f"AVENCER_{data_str}{extensao}",
            'alunos':   Path(caminho).name,   # mantém nome original
        }
        nome_destino = nomes_padrao[tipo]

        # Copiar para BASE DE DADOS / Ano / Mês / Dia com nome padronizado
        pasta_destino = get_pasta_data(BASE_DE_DADOS_DIR)
        destino = pasta_destino / nome_destino
        shutil.copy2(caminho, destino)

        # Atualizar path e label
        setattr(self, f'path_{tipo}', destino)
        label = getattr(self, f'label_{tipo}')
        label.config(text=self._texto_arquivo(destino))

        caminho_rel = destino.relative_to(PROJETO_DIR)
        self.atualizar_status(f"✅ Importado: {Path(caminho).name}  →  {caminho_rel}")
        self.log(f"Arquivo importado: {destino}")

    # ------------------------------------------------------------------
    # ABRIR PASTA DE RELATÓRIOS
    # ------------------------------------------------------------------

    def abrir_relatorios(self):
        """Abre a pasta de relatórios de hoje no Explorer."""
        pasta = get_pasta_data(RELATORIOS_DIR)
        os.startfile(str(pasta))

    # ------------------------------------------------------------------
    # CONSOLIDAÇÃO
    # ------------------------------------------------------------------

    def consolidar_vencidas(self):
        """Consolida os dados de vencidas."""
        try:
            self.atualizar_status("⏳ Carregando arquivos...")

            if not self.path_vencidos or not Path(self.path_vencidos).exists():
                raise FileNotFoundError("Selecione o arquivo de Vencidos antes de consolidar.")
            if not self.path_alunos or not Path(self.path_alunos).exists():
                raise FileNotFoundError("Selecione o arquivo de Alunos antes de consolidar.")

            vencidos_path = Path(self.path_vencidos)
            alunos_path   = Path(self.path_alunos)

            # Carregar VENCIDOS (tenta encodings, separadores e com/sem linha de título)
            self.atualizar_status(f"📂 Lendo {vencidos_path.name}...")
            self.vencidos = None
            for enc in ['utf-8', 'latin1', 'cp1252']:
                for sep in [',', ';', '\t']:
                    for skip in [0, 1]:
                        try:
                            df = pd.read_csv(str(vencidos_path), encoding=enc, sep=sep, skiprows=skip)
                            if 'Aluno' in df.columns:
                                self.vencidos = df
                                break
                        except Exception:
                            pass
                    if self.vencidos is not None:
                        break
                if self.vencidos is not None:
                    break

            if self.vencidos is None or 'Aluno' not in self.vencidos.columns:
                colunas = list(self.vencidos.columns) if self.vencidos is not None else []
                raise ValueError(
                    f"Não consegui ler o arquivo de Vencidos.\n"
                    f"Colunas encontradas: {colunas}\n"
                    f"Verifique se é o arquivo correto exportado do Synapta."
                )

            # Carregar ALUNOS
            self.atualizar_status(f"📂 Lendo {alunos_path.name}...")
            self.alunos = None
            for enc in ['utf-8', 'latin1']:
                for sep in [',', ';', '\t']:
                    try:
                        df = pd.read_csv(str(alunos_path), encoding=enc, sep=sep)
                        if 'CPF' in df.columns:
                            self.alunos = df
                            break
                    except Exception:
                        pass
                if self.alunos is not None:
                    break

            if self.alunos is None or 'CPF' not in self.alunos.columns:
                raise ValueError(
                    "Não consegui ler o arquivo de Alunos.\n"
                    "Verifique se é o arquivo correto."
                )

            # Processar VENCIDOS
            self.atualizar_status("🔧 Processando dados...")
            self.vencidos['Aluno'] = self.vencidos['Aluno'].str.strip()
            self.vencidos['CPF sem mask'] = (
                self.vencidos['CPF sem mask'].astype(str).str.strip().str.zfill(11)
            )
            self.vencidos['Vencimento'] = pd.to_datetime(
                self.vencidos['Vencimento'], format='%d/%m/%Y'
            )

            def converter_valor(val):
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

            self.vencidos['Total'] = self.vencidos['Total'].apply(converter_valor)

            # Consolidar por CPF
            self.atualizar_status("🔄 Consolidando por aluno...")
            self.consolidacao = self.vencidos.groupby('CPF sem mask').agg({
                'Aluno':    'first',
                'Fatura #': 'count',
                'Vencimento': 'max',
                'Total':    'sum',
            }).reset_index()
            self.consolidacao.columns = ['CPF', 'Aluno', 'Qtd_Boletos', 'Ultimo_Vencimento', 'Total']

            # Join com dados de contato
            self.atualizar_status("🔗 Trazendo dados de contato...")
            self.alunos['CPF_sem_mask'] = (
                self.alunos['CPF']
                .str.replace('.', '', regex=False)
                .str.replace('-', '', regex=False)
                .str.strip()
                .str.zfill(11)
            )
            self.consolidacao = self.consolidacao.merge(
                self.alunos[['CPF_sem_mask', 'E-mail', 'Telefone']],
                left_on='CPF', right_on='CPF_sem_mask', how='left',
            )

            # Classificar por categoria
            self.atualizar_status("📊 Classificando categorias...")
            hoje = pd.Timestamp.now()
            self.consolidacao['Dias_Atraso'] = (
                hoje - self.consolidacao['Ultimo_Vencimento']
            ).dt.days

            def classificar(row):
                if row['Qtd_Boletos'] == 1 and row['Dias_Atraso'] < 30:
                    return 'A (Inadimplente Novo)'
                return 'B (Demais Inadimplentes)'

            self.consolidacao['Categoria'] = self.consolidacao.apply(classificar, axis=1)
            self.consolidacao = self.consolidacao.sort_values('Ultimo_Vencimento')

            self.atualizar_tabela()

            total_a     = len(self.consolidacao[self.consolidacao['Categoria'] == 'A (Inadimplente Novo)'])
            total_b     = len(self.consolidacao[self.consolidacao['Categoria'] == 'B (Demais Inadimplentes)'])
            valor_total = self.consolidacao['Total'].sum()

            info = (
                f"✅ Consolidação OK | Total: {len(self.consolidacao)} alunos | "
                f"Cat. A: {total_a} | Cat. B: {total_b} | "
                f"Valor: R$ {valor_total:,.2f}"
            )
            self.atualizar_status(info)
            self.info_label.config(text=info)
            self.log(f"Consolidação concluída: {len(self.consolidacao)} alunos")

            messagebox.showinfo("Sucesso",
                f"Consolidação concluída!\n\n"
                f"Total: {len(self.consolidacao)} alunos\n"
                f"Categoria A (Inadimplentes Novos): {total_a}\n"
                f"Categoria B (Demais Inadimplentes): {total_b}\n"
                f"Valor Total: R$ {valor_total:,.2f}"
            )

        except Exception as e:
            self.log(f"ERRO: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao consolidar:\n{str(e)}")
            self.atualizar_status(f"❌ Erro: {str(e)}")

    # ------------------------------------------------------------------
    # TABELA
    # ------------------------------------------------------------------

    def atualizar_tabela(self):
        """Atualiza a tabela com os dados da consolidação."""
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        if self.consolidacao is None:
            return

        for _, row in self.consolidacao.iterrows():
            nome      = row['Aluno'][:40]
            qtd       = int(row['Qtd_Boletos'])
            valor     = f"R$ {row['Total']:,.2f}"
            categoria = row['Categoria']
            tags      = ('cat_a',) if categoria == 'A (Inadimplente Novo)' else ('cat_b',)
            self.tabela.insert('', 'end', values=(nome, qtd, valor, categoria), tags=tags)

        self.tabela.tag_configure('cat_a', background='#E3F2FD')   # azul claro
        self.tabela.tag_configure('cat_b', background='#FFEBEE')   # vermelho claro

    # ------------------------------------------------------------------
    # VISUALIZAR RESULTADO
    # ------------------------------------------------------------------

    def visualizar_resultado(self):
        """Abre janela com resumo estatístico."""
        if self.consolidacao is None:
            messagebox.showwarning("Aviso", "Primeiro consolide as vencidas!")
            return

        janela = tk.Toplevel(self.root)
        janela.title("Resultado da Consolidação")
        janela.geometry("700x420")

        total_a = len(self.consolidacao[self.consolidacao['Categoria'] == 'A (Inadimplente Novo)'])
        total_b = len(self.consolidacao[self.consolidacao['Categoria'] == 'B (Demais Inadimplentes)'])

        info_text = (
            f"\n"
            f"  RESUMO DA CONSOLIDAÇÃO\n"
            f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"  ESTATÍSTICAS GERAIS:\n"
            f"  ├─ Total de alunos:                  {len(self.consolidacao)}\n"
            f"  ├─ Categoria A (Inadimplentes Novos): {total_a}\n"
            f"  ├─ Categoria B (Demais Inadimplentes):{total_b}\n"
            f"  ├─ Valor total em atraso:             R$ {self.consolidacao['Total'].sum():,.2f}\n"
            f"  ├─ Valor médio por aluno:             R$ {self.consolidacao['Total'].mean():,.2f}\n"
            f"  └─ Maior inadimplência:               R$ {self.consolidacao['Total'].max():,.2f}\n\n"
            f"  COBERTURA DE CONTATO:\n"
            f"  ├─ Com E-mail:    {self.consolidacao['E-mail'].notna().sum()}\n"
            f"  └─ Com Telefone:  {self.consolidacao['Telefone'].notna().sum()}\n"
        )

        ttk.Label(janela, text=info_text, justify=tk.LEFT, font=("Courier", 10)).pack(
            fill=tk.BOTH, expand=True, padx=10, pady=10
        )

    # ------------------------------------------------------------------
    # GERAÇÃO DE RELATÓRIOS
    # ------------------------------------------------------------------

    def gerar_relatorio(self):
        """Gera relatórios TXT e XLSX separados por categoria na pasta datada."""
        if self.consolidacao is None:
            messagebox.showwarning("Aviso", "Primeiro consolide as vencidas!")
            return

        try:
            self.atualizar_status("📄 Gerando relatórios...")

            pasta_saida = get_pasta_data(RELATORIOS_DIR)
            data_str    = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

            cat_a = self.consolidacao[self.consolidacao['Categoria'] == 'A (Inadimplente Novo)']
            cat_b = self.consolidacao[self.consolidacao['Categoria'] == 'B (Demais Inadimplentes)']

            if len(cat_a) > 0:
                self.atualizar_status("📝 Gerando Categoria A (TXT + XLSX)...")
                self.gerar_txt_categoria('A', cat_a, data_str, pasta_saida)
                self.gerar_xlsx_categoria('A', cat_a, data_str, pasta_saida)

            if len(cat_b) > 0:
                self.atualizar_status("📝 Gerando Categoria B (TXT + XLSX)...")
                self.gerar_txt_categoria('B', cat_b, data_str, pasta_saida)
                self.gerar_xlsx_categoria('B', cat_b, data_str, pasta_saida)

            caminho_rel = pasta_saida.relative_to(PROJETO_DIR)
            self.atualizar_status(f"✅ Relatórios gerados em: {caminho_rel}")
            self.log("Relatórios gerados com sucesso")

            msg = f"Relatórios gerados em:\n{pasta_saida}\n\n"
            if len(cat_a) > 0:
                msg += f"✓ Categoria A — Inadimplentes Novos ({len(cat_a)} alunos)\n"
            if len(cat_b) > 0:
                msg += f"✓ Categoria B — Demais Inadimplentes ({len(cat_b)} alunos)\n"

            messagebox.showinfo("Sucesso", msg)

        except Exception as e:
            self.log(f"ERRO ao gerar relatórios: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao gerar relatórios:\n{str(e)}")

    def gerar_txt_categoria(self, categoria, dados, data_str, pasta_saida):
        """Gera arquivo TXT com mensagens prontas para WhatsApp."""
        if categoria == 'A':
            titulo    = "CATEGORIA A — INADIMPLENTES NOVOS (1 título, vencido há <30 dias)"
            frequencia = "Enviar DIARIAMENTE"
        else:
            titulo    = "CATEGORIA B — DEMAIS INADIMPLENTES"
            frequencia = "Enviar 1X POR SEMANA"

        linhas = [
            "=" * 70,
            f"RELATÓRIO DE MENSAGENS — {titulo}",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Frequência: {frequencia}",
            f"Total: {len(dados)} alunos",
            "=" * 70,
        ]

        for _, row in dados.iterrows():
            nome         = row['Aluno']
            telefone     = row['Telefone'] if pd.notna(row['Telefone']) else "N/A"
            vencimento   = row['Ultimo_Vencimento'].strftime('%d/%m/%Y')
            dias_atraso  = int(row['Dias_Atraso'])
            primeiro_nome = nome.split()[0].capitalize()
            tratamento   = detectar_tratamento(nome)

            if categoria == 'A':
                mensagem = MENSAGEM_A.format(
                    TRATAMENTO=tratamento, NOME=primeiro_nome, DATA_VENCIMENTO=vencimento
                )
            else:
                mensagem = MENSAGEM_B.format(TRATAMENTO=tratamento, NOME=primeiro_nome)

            linhas += [
                f"\nAluno: {nome}",
                f"Telefone: {telefone}",
                f"Dias de Atraso: {dias_atraso}",
                f"Valor: R$ {row['Total']:,.2f}",
                "\nMensagem:",
                mensagem,
                "-" * 70,
            ]

        linhas += ["\n" + "=" * 70, "FIM DO RELATÓRIO", "=" * 70]

        arquivo = pasta_saida / f"relatorio_categoria_{categoria}_{data_str}.txt"
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas))
        self.log(f"TXT gerado: {arquivo}")

    def gerar_xlsx_categoria(self, categoria, dados, data_str, pasta_saida):
        """Gera arquivo XLSX com dados da categoria."""
        df_export = dados[[
            'Aluno', 'Telefone', 'E-mail', 'Qtd_Boletos',
            'Total', 'Ultimo_Vencimento', 'Dias_Atraso', 'Categoria'
        ]].copy()

        df_export.columns = [
            'Nome Aluno', 'Telefone', 'E-mail', 'Qtd Títulos',
            'Valor Total', 'Último Vencimento', 'Dias de Atraso', 'Categoria'
        ]
        df_export['Último Vencimento'] = df_export['Último Vencimento'].dt.strftime('%d/%m/%Y')
        df_export['Valor Total'] = df_export['Valor Total'].apply(lambda x: f'R$ {x:,.2f}')

        arquivo = pasta_saida / f"relatorio_categoria_{categoria}_{data_str}.xlsx"
        df_export.to_excel(arquivo, index=False, sheet_name='Relatório')
        self.log(f"XLSX gerado: {arquivo}")

    # ------------------------------------------------------------------
    # GESTÃO DE BASE DE INADIMPLENTES
    # ------------------------------------------------------------------

    def _status_base(self):
        """Texto de status da base persistente."""
        if BASE_INADIMPLENTES.exists():
            try:
                base = pd.read_excel(BASE_INADIMPLENTES)
                data_mod = datetime.fromtimestamp(BASE_INADIMPLENTES.stat().st_mtime)
                return (f"✅ Base ativa: {len(base)} inadimplentes | "
                        f"Última atualização: {data_mod.strftime('%d/%m/%Y %H:%M')}")
            except Exception:
                pass
        return "⚠️  Base ainda não criada — rode 'Comparar e Atualizar Base' após consolidar"

    def comparar_e_atualizar_base(self):
        """Compara consolidação atual com a base persistente e gera relatórios de diferença."""
        if self.consolidacao is None:
            messagebox.showwarning("Aviso", "Primeiro consolide as vencidas antes de atualizar a base!")
            return

        try:
            self.atualizar_status("🔄 Comparando com a base de inadimplentes...")

            # ── Carregar base existente ──────────────────────────────────────
            if BASE_INADIMPLENTES.exists():
                base_anterior = pd.read_excel(BASE_INADIMPLENTES)
                base_anterior['CPF'] = base_anterior['CPF'].astype(str).str.zfill(11)
                cpfs_base = set(base_anterior['CPF'])
                self.atualizar_status(f"📂 Base carregada: {len(base_anterior)} registros")
            else:
                base_anterior = pd.DataFrame()
                cpfs_base = set()
                self.atualizar_status("📂 Base ainda não existe — será criada agora")

            # ── CPFs do novo relatório de vencidos ───────────────────────────
            nova_cons = self.consolidacao.copy()
            nova_cons['CPF'] = nova_cons['CPF'].astype(str).str.zfill(11)
            cpfs_novo = set(nova_cons['CPF'])

            # ── Classificação das diferenças ─────────────────────────────────
            # Saiu dos vencidos = quitou OU renegociou — Luana revisa manualmente
            cpfs_novos_inad = cpfs_novo - cpfs_base
            cpfs_quitados   = cpfs_base - cpfs_novo

            novos     = nova_cons[nova_cons['CPF'].isin(cpfs_novos_inad)]
            quitados  = (base_anterior[base_anterior['CPF'].isin(cpfs_quitados)]
                         if not base_anterior.empty else pd.DataFrame())
            continuam = nova_cons[nova_cons['CPF'].isin(cpfs_base & cpfs_novo)]

            self.atualizar_status(
                f"📊 Novos: {len(novos)} | Saíram dos vencidos: {len(quitados)} | "
                f"Continuam: {len(continuam)}"
            )

            # ── Gerar relatórios de diferença ────────────────────────────────
            pasta_saida = get_pasta_data(RELATORIOS_DIR)
            data_str    = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

            if len(novos) > 0:
                self.atualizar_status("📝 Gerando relatório de NOVOS INADIMPLENTES...")
                self._gerar_relatorio_novos(novos, data_str, pasta_saida)

            if len(quitados) > 0:
                self.atualizar_status("📝 Gerando relatório de SAÍRAM DOS VENCIDOS...")
                self._gerar_relatorio_quitados(quitados, data_str, pasta_saida)

            # ── Construir nova base ──────────────────────────────────────────
            nova_base = nova_cons[[
                'CPF', 'Aluno', 'Telefone', 'E-mail',
                'Qtd_Boletos', 'Total', 'Ultimo_Vencimento', 'Dias_Atraso', 'Categoria'
            ]].copy()
            nova_base['Ultimo_Vencimento'] = nova_base['Ultimo_Vencimento'].dt.strftime('%d/%m/%Y')

            hoje_str = datetime.now().strftime('%d/%m/%Y')
            if not base_anterior.empty and 'Data_Entrada' in base_anterior.columns:
                nova_base = nova_base.merge(
                    base_anterior[['CPF', 'Data_Entrada']], on='CPF', how='left'
                )
                nova_base['Data_Entrada'] = nova_base['Data_Entrada'].fillna(hoje_str)
            else:
                nova_base['Data_Entrada'] = hoje_str

            nova_base = nova_base[[
                'CPF', 'Aluno', 'Telefone', 'E-mail',
                'Qtd_Boletos', 'Total', 'Ultimo_Vencimento',
                'Dias_Atraso', 'Categoria', 'Data_Entrada'
            ]]

            # ── Substituir base ──────────────────────────────────────────────
            nova_base.to_excel(BASE_INADIMPLENTES, index=False, sheet_name='Base Inadimplentes')
            self.log(f"Base atualizada: {len(nova_base)} inadimplentes → {BASE_INADIMPLENTES}")

            # ── Atualizar label de status da base ────────────────────────────
            self.label_base_status.config(text=self._status_base())

            self.atualizar_status(f"✅ Base atualizada com {len(nova_base)} inadimplentes")

            # ── Resumo final ─────────────────────────────────────────────────
            msg = (
                f"Base de Inadimplentes atualizada!\n\n"
                f"🔴 NOVOS INADIMPLENTES:  {len(novos)}\n"
                f"   → Adicionar tag no CRM\n\n"
                f"🟡 SAÍRAM DOS VENCIDOS:  {len(quitados)}\n"
                f"   → Verificar: Pagou (remover tag) ou Renegociou (manter tag)\n"
                f"   → Ver relatório QUITADOS_{data_str}.xlsx\n\n"
                f"🟢 CONTINUAM:            {len(continuam)}\n\n"
                f"📁 Relatórios salvos em:\n{pasta_saida}"
            )
            messagebox.showinfo("Gestão de Base — Concluída", msg)

        except Exception as e:
            self.log(f"ERRO ao atualizar base: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao atualizar base:\n{str(e)}")
            self.atualizar_status(f"❌ Erro: {str(e)}")

    def _gerar_relatorio_novos(self, dados, data_str, pasta_saida):
        """Gera TXT e XLSX dos novos inadimplentes (adicionar tag no CRM)."""
        # TXT
        linhas = [
            "=" * 70,
            "NOVOS INADIMPLENTES — ADICIONAR TAG NO CRM",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Total: {len(dados)} alunos",
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
                f"\nAluno:      {row['Aluno']}",
                f"CPF:        {row['CPF']}",
                f"Telefone:   {telefone}",
                f"E-mail:     {email}",
                f"Qtd Títulos:{int(row['Qtd_Boletos'])}",
                f"Valor:      R$ {row['Total']:,.2f}",
                f"Últ. Venc.: {venc}",
                "-" * 70,
            ]
        linhas += ["\n" + "=" * 70, "FIM DO RELATÓRIO", "=" * 70]

        arq_txt = pasta_saida / f"NOVOS_INADIMPLENTES_{data_str}.txt"
        with open(arq_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas))

        # XLSX
        df = dados[['CPF', 'Aluno', 'Telefone', 'E-mail',
                    'Qtd_Boletos', 'Total', 'Ultimo_Vencimento', 'Categoria']].copy()
        df.columns = ['CPF', 'Nome Aluno', 'Telefone', 'E-mail',
                      'Qtd Títulos', 'Valor Total', 'Último Vencimento', 'Categoria']
        if hasattr(df['Último Vencimento'].iloc[0], 'strftime'):
            df['Último Vencimento'] = df['Último Vencimento'].dt.strftime('%d/%m/%Y')
        df['Valor Total'] = df['Valor Total'].apply(lambda x: f'R$ {x:,.2f}')
        df['Ação CRM'] = 'ADICIONAR TAG INADIMPLENTE'

        arq_xlsx = pasta_saida / f"NOVOS_INADIMPLENTES_{data_str}.xlsx"
        df.to_excel(arq_xlsx, index=False, sheet_name='Novos Inadimplentes')
        self.log(f"Relatório NOVOS gerado: {arq_xlsx}")

    def _gerar_relatorio_quitados(self, dados, data_str, pasta_saida):
        """Gera TXT e XLSX dos alunos que saíram dos vencidos (quitados ou renegociados)."""
        # TXT
        linhas = [
            "=" * 70,
            "SAÍRAM DOS VENCIDOS — REVISAR: QUITADOS OU RENEGOCIADOS",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Total: {len(dados)} alunos",
            "ATENCAO: Verificar manualmente se cada aluno PAGOU ou RENEGOCIOU.",
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
                f"\nAluno:      {row['Aluno']}",
                f"CPF:        {row['CPF']}",
                f"Telefone:   {telefone}",
                f"E-mail:     {email}",
                f"Situacao:   [ ] Pagou - remover tag   [ ] Renegociou - manter tag",
                "-" * 70,
            ]
        linhas += ["\n" + "=" * 70, "FIM DO RELATÓRIO", "=" * 70]

        arq_txt = pasta_saida / f"QUITADOS_{data_str}.txt"
        with open(arq_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas))

        # XLSX — coluna "Situação" em branco para Luana preencher
        colunas_disponiveis = [c for c in
            ['CPF', 'Aluno', 'Telefone', 'E-mail', 'Data_Entrada', 'Categoria']
            if c in dados.columns]
        df = dados[colunas_disponiveis].copy()
        df['Situacao']  = ''
        df['Acao CRM']  = 'VERIFICAR — Pagou (remover tag) ou Renegociou (manter tag)'

        arq_xlsx = pasta_saida / f"QUITADOS_{data_str}.xlsx"
        df.to_excel(arq_xlsx, index=False, sheet_name='Saíram dos Vencidos')
        self.log(f"Relatório QUITADOS gerado: {arq_xlsx}")

    # ------------------------------------------------------------------
    # UTILITÁRIOS
    # ------------------------------------------------------------------

    def limpar(self):
        """Limpa dados e interface."""
        self.vencidos     = None
        self.alunos       = None
        self.consolidacao = None
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        self.atualizar_status("🗑️ Dados limpos")
        self.info_label.config(text="Pronto para consolidar")
        self.log("Dados limpos")

    def atualizar_status(self, texto):
        """Adiciona linha no campo de status."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{texto}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()

    def log(self, mensagem):
        """Grava linha no log em disco."""
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        log_msg   = f"[{timestamp}] {mensagem}"
        print(log_msg)
        arquivo_log = LOGS_DIR / "app.log"
        with open(arquivo_log, 'a', encoding='utf-8') as f:
            f.write(log_msg + "\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacaoInadimplencia(root)
    root.mainloop()
