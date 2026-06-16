"""Testes do upload stateless (EPIC-02 Onda 4).

Cobre: migration 010 (up/down), staging de uploads no banco (round-trip, substituição,
isolamento por empresa, status, limpeza), leitura em memória pelo `processing._ler_csv`
e o fluxo de rota ponta a ponta (importar → consolidar → baixar relatórios em ZIP) sem
tocar o disco.
"""
import io
import sqlite3
import zipfile

import processing as proc


def _tabelas(conn) -> set:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return {r[0] for r in rows}


# CSV mínimos no formato Synapta (mesma forma usada em test_processing).
_VENCIDOS_CSV = (
    "Aluno,CPF sem mask,Vencimento,Total,Fatura #\n"
    'Maria Silva,12345678901,01/01/2020,"R$ 1.000,00",1\n'
).encode('utf-8')

_ALUNOS_CSV = (
    "CPF,E-mail,Telefone\n"
    "123.456.789-01,maria@x.com,11999998888\n"
).encode('utf-8')


# ── Migration 010 ────────────────────────────────────────────────────────────

def test_migration_010_up_down(tmp_path, db):
    """A migration 010 cria e remove a tabela uploads_staging (up/down)."""
    mods = {m.version: m for m in db.runner.discover(db.MIGRATIONS_DIR)}
    m010 = mods[10]
    assert m010.name == 'add_uploads_staging'

    conn = sqlite3.connect(str(tmp_path / 'm010.db'))
    try:
        m010.up(conn)
        assert 'uploads_staging' in _tabelas(conn)
        cols = {r[1] for r in conn.execute("PRAGMA table_info(uploads_staging)").fetchall()}
        assert {'empresa', 'tipo', 'filename', 'conteudo'}.issubset(cols)

        m010.down(conn)
        assert 'uploads_staging' not in _tabelas(conn)
    finally:
        conn.close()


# ── Staging no banco ─────────────────────────────────────────────────────────

def test_staging_round_trip(db):
    """Grava e lê de volta os bytes exatos do arquivo."""
    db.limpar_upload_staging('INEPROTEC')
    db.salvar_upload_staging('INEPROTEC', 'vencidos', 'fat.csv', _VENCIDOS_CSV)
    item = db.carregar_upload_staging('INEPROTEC', 'vencidos')
    assert item is not None
    filename, conteudo = item
    assert filename == 'fat.csv'
    assert conteudo == _VENCIDOS_CSV
    assert isinstance(conteudo, bytes)


def test_staging_substitui_no_reupload(db):
    """Re-upload do mesmo tipo substitui o arquivo anterior (PK empresa+tipo)."""
    db.limpar_upload_staging('INEPROTEC')
    db.salvar_upload_staging('INEPROTEC', 'vencidos', 'velho.csv', b'antigo')
    db.salvar_upload_staging('INEPROTEC', 'vencidos', 'novo.csv', b'novo')
    filename, conteudo = db.carregar_upload_staging('INEPROTEC', 'vencidos')
    assert filename == 'novo.csv'
    assert conteudo == b'novo'
    # Apenas 1 linha para (empresa, tipo).
    with db.get_conn() as conn:
        n = conn.execute(
            "SELECT COUNT(*) FROM uploads_staging WHERE empresa=? AND tipo=?",
            ('INEPROTEC', 'vencidos')).fetchone()[0]
    assert n == 1


def test_staging_isolado_por_empresa(db):
    """O staging de uma empresa não vaza para a outra."""
    db.limpar_upload_staging('INEPROTEC')
    db.limpar_upload_staging('MATRICULAEAD')
    db.salvar_upload_staging('INEPROTEC', 'alunos', 'a.csv', b'ine')
    assert db.carregar_upload_staging('MATRICULAEAD', 'alunos') is None
    assert db.carregar_upload_staging('INEPROTEC', 'alunos')[1] == b'ine'


def test_staging_status_e_limpeza(db):
    """status_uploads_staging lista os tipos presentes; limpar remove um ou todos."""
    db.limpar_upload_staging('INEPROTEC')
    db.salvar_upload_staging('INEPROTEC', 'vencidos', 'v.csv', b'v')
    db.salvar_upload_staging('INEPROTEC', 'alunos', 'a.csv', b'a')
    status = db.status_uploads_staging('INEPROTEC')
    assert status == {'vencidos': 'v.csv', 'alunos': 'a.csv'}

    db.limpar_upload_staging('INEPROTEC', 'vencidos')
    assert db.status_uploads_staging('INEPROTEC') == {'alunos': 'a.csv'}

    db.limpar_upload_staging('INEPROTEC')
    assert db.status_uploads_staging('INEPROTEC') == {}


# ── Leitura em memória ───────────────────────────────────────────────────────

def test_ler_csv_de_buffer(db):
    """_ler_csv lê de (BytesIO, filename) sem tocar o disco."""
    df = proc._ler_csv((io.BytesIO(_ALUNOS_CSV), 'alunos.csv'), 'CPF')
    assert df is not None
    assert 'CPF' in df.columns


def test_ler_csv_buffer_separador_e_reuso(db):
    """Detecta ';' a partir do buffer e o mesmo buffer pode ser relido (seek interno)."""
    conteudo = ("Aluno;CPF sem mask;Vencimento;Total;Fatura #\n"
                "Ana;12345678901;01/01/2020;100,00;1\n").encode('utf-8')
    buf = io.BytesIO(conteudo)
    df1 = proc._ler_csv((buf, 'x.csv'), 'Aluno')
    df2 = proc._ler_csv((buf, 'x.csv'), 'Aluno')  # reuso do mesmo buffer
    assert df1 is not None and df2 is not None
    assert df1.iloc[0]['Aluno'] == 'Ana'


# ── Fluxo de rota ponta a ponta ──────────────────────────────────────────────

def test_upload_vai_para_staging_sem_disco(client, db, users, login):
    """POST /upload grava no banco e não cria pasta de uploads em disco."""
    login('admin', 'admin123')
    db.limpar_upload_staging('INEPROTEC')
    db.limpar_estado_blob('INEPROTEC')  # garante o branch "sem consolidação" no índice
    data = {'tipo': 'vencidos',
            'arquivo': (io.BytesIO(_VENCIDOS_CSV), 'faturas.csv')}
    client.post('/upload', data=data, content_type='multipart/form-data',
                follow_redirects=True)
    item = db.carregar_upload_staging('INEPROTEC', 'vencidos')
    assert item is not None and item[0] == 'faturas.csv'
    # Nenhuma pasta de uploads é criada no filesystem (stateless).
    assert not (db.DATA_DIR / 'uploads').exists()


def test_upload_formato_invalido_rejeitado(client, db, users, login):
    """Extensão fora de .csv/.xlsx/.xls é recusada."""
    login('admin', 'admin123')
    db.limpar_upload_staging('INEPROTEC')
    db.limpar_estado_blob('INEPROTEC')  # garante o branch "sem consolidação" no índice
    data = {'tipo': 'vencidos', 'arquivo': (io.BytesIO(b'x'), 'nota.txt')}
    html = client.post('/upload', data=data, content_type='multipart/form-data',
                       follow_redirects=True).get_data(as_text=True)
    assert 'Formato inválido' in html
    assert db.carregar_upload_staging('INEPROTEC', 'vencidos') is None


def test_consolidar_le_do_staging(client, db, users, login):
    """Importar vencidos+alunos para o staging e consolidar lendo da memória."""
    login('admin', 'admin123')
    db.limpar_upload_staging('INEPROTEC')
    db.limpar_estado_blob('INEPROTEC')
    db.salvar_upload_staging('INEPROTEC', 'vencidos', 'v.csv', _VENCIDOS_CSV)
    db.salvar_upload_staging('INEPROTEC', 'alunos', 'a.csv', _ALUNOS_CSV)

    html = client.post('/consolidar', follow_redirects=True).get_data(as_text=True)
    assert 'Maria Silva' in html
    assert db.estado_existe('INEPROTEC')


def test_gerar_relatorio_devolve_zip(client, db, users, login):
    """Com consolidação + template, /gerar-relatorio entrega um ZIP para download."""
    login('admin', 'admin123')
    db.limpar_upload_staging('INEPROTEC')
    db.limpar_estado_blob('INEPROTEC')
    db.salvar_upload_staging('INEPROTEC', 'vencidos', 'v.csv', _VENCIDOS_CSV)
    db.salvar_upload_staging('INEPROTEC', 'alunos', 'a.csv', _ALUNOS_CSV)
    # Template que cobre qualquer atraso (>= 0 dias) para garantir um arquivo gerado.
    db.criar_template('Cobranca Teste', 'Olá {NOME}', 'INEPROTEC', 0, None, 'TAG_TESTE')
    client.post('/consolidar', follow_redirects=True)

    resp = client.post('/gerar-relatorio')
    assert resp.status_code == 200
    assert resp.mimetype == 'application/zip'
    # O ZIP tem ao menos um arquivo de relatório dentro.
    zf = zipfile.ZipFile(io.BytesIO(resp.get_data()))
    assert any(n.endswith(('.txt', '.xlsx')) for n in zf.namelist())
