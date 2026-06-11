"""Testes do processing.py — funções puras e a consolidação end-to-end."""
import pytest

import processing as proc


# ── Formatação de moeda (BRL) ────────────────────────────────────────────────

@pytest.mark.parametrize("valor,esperado", [
    (1957.81, "R$ 1.957,81"),
    (1024.62, "R$ 1.024,62"),
    (0, "R$ 0,00"),
    (1000000, "R$ 1.000.000,00"),
    (5.5, "R$ 5,50"),
])
def test_fmt_brl(valor, esperado):
    assert proc.fmt_brl(valor) == esperado


# ── Conversão de valor brasileiro → float ────────────────────────────────────

@pytest.mark.parametrize("entrada,esperado", [
    ("R$ 1.024,62", 1024.62),
    ("1.234.567,89", 1234567.89),
    ("500,50", 500.50),
    ("500", 500.0),
    ("", 0.0),
    (None, 0.0),
    ("texto invalido", 0.0),
])
def test_converter_valor(entrada, esperado):
    assert proc._converter_valor(entrada) == pytest.approx(esperado)


# ── Heurística de tratamento (sr./sra.) ──────────────────────────────────────

@pytest.mark.parametrize("nome,esperado", [
    ("Maria Silva", "Sra."),
    ("João Souza", "Sr."),
    ("Ana Paula", "Sra."),
    ("Carlos Eduardo", "Sr."),
    ("Joshua Lima", "Sr."),      # exceção masculina (termina em 'a')
    ("Rachel Costa", "Sra."),    # exceção feminina (não termina em 'a')
])
def test_detectar_tratamento(nome, esperado):
    assert proc.detectar_tratamento(nome) == esperado


# ── _SafeFormat: mantém placeholders desconhecidos ───────────────────────────

def test_safeformat_preserva_desconhecidos():
    template = "Olá {NOME}, link: {LINK_PAGAMENTO}"
    saida = template.format_map(proc._SafeFormat(NOME="Maria"))
    assert saida == "Olá Maria, link: {LINK_PAGAMENTO}"


def test_slugify():
    assert proc._slugify("Vencidos - 2 a 29 Dias!") == "vencidos_2_a_29_dias"


# ── consolidar(): pipeline completo com arquivos temporários ─────────────────

def _escrever(tmp_path, nome, conteudo):
    p = tmp_path / nome
    p.write_text(conteudo, encoding='utf-8')
    return p


def test_consolidar_basico(tmp_path):
    vencidos = _escrever(tmp_path, "vencidos.csv",
        "Aluno,CPF sem mask,Vencimento,Total,Fatura #\n"
        'Maria Silva,12345678901,01/01/2020,"R$ 1.000,00",1\n'
        'João Souza,98765432100,01/01/2020,"R$ 500,50",2\n'
    )
    alunos = _escrever(tmp_path, "alunos.csv",
        "CPF,E-mail,Telefone\n"
        "123.456.789-01,maria@x.com,11999998888\n"
        "987.654.321-00,joao@x.com,11888887777\n"
    )

    consolidado, stats = proc.consolidar(vencidos, alunos)

    assert stats['total'] == 2
    assert stats['valor_total'] == pytest.approx(1500.50)
    # Vencimento de 2020 → muito acima de 30 dias
    assert set(consolidado['Categoria']) == {'Acima 30 Dias'}
    assert stats['cat_acima30'] == 2
    assert stats['com_email'] == 2
    assert stats['com_telefone'] == 2
    assert stats['sem_cadastro'] == 0


def test_consolidar_sem_cadastro(tmp_path):
    """Aluno nos vencidos sem match no cadastro entra em 'sem_cadastro'."""
    vencidos = _escrever(tmp_path, "vencidos.csv",
        "Aluno,CPF sem mask,Vencimento,Total,Fatura #\n"
        'Maria Silva,12345678901,01/01/2020,"R$ 1.000,00",1\n'
        'Fulano Sem Cadastro,11122233344,01/01/2020,"R$ 200,00",2\n'
    )
    alunos = _escrever(tmp_path, "alunos.csv",
        "CPF,E-mail,Telefone\n"
        "123.456.789-01,maria@x.com,11999998888\n"
    )

    _, stats = proc.consolidar(vencidos, alunos)
    assert stats['sem_cadastro'] == 1
    assert "Fulano Sem Cadastro" in stats['sem_cadastro_nomes']


def test_consolidar_separador_ponto_e_virgula(tmp_path):
    """_ler_csv deve detectar o separador ';' automaticamente."""
    vencidos = _escrever(tmp_path, "vencidos.csv",
        "Aluno;CPF sem mask;Vencimento;Total;Fatura #\n"
        "Ana Paula;12345678901;01/01/2020;100,00;1\n"
    )
    alunos = _escrever(tmp_path, "alunos.csv",
        "CPF;E-mail;Telefone\n"
        "123.456.789-01;ana@x.com;11999990000\n"
    )
    consolidado, stats = proc.consolidar(vencidos, alunos)
    assert stats['total'] == 1
    assert consolidado.iloc[0]['Aluno'] == "Ana Paula"


def test_consolidar_arquivo_invalido(tmp_path):
    """Arquivo sem a coluna esperada deve lançar ValueError legível."""
    ruim = _escrever(tmp_path, "ruim.csv", "coluna_qualquer\nvalor\n")
    alunos = _escrever(tmp_path, "alunos.csv", "CPF,E-mail,Telefone\n123,a@x.com,11\n")
    with pytest.raises(ValueError):
        proc.consolidar(ruim, alunos)
