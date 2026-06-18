"""Testes da fundação backend da STORY-H-01 (WhatsApp via Google Drive + Kommo).

Cobre: migration 008 (up/down + runner), config_whatsapp (round-trip com credencial
fora do banco), o módulo gdrive (degradação graciosa + lógica create/replace) e as
rotas da Onda 2 (UI + fluxo: configurar, testar, exportar).
"""
import io
import os
import sqlite3

import pandas as pd
import pytest

import gdrive


def _tabelas(conn) -> set:
    """Lista tabelas do banco — cross-dialect (Onda 6)."""
    if os.environ.get('TEST_DIALECT') == 'postgres':
        rows = conn.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname='public'"
        ).fetchall()
        return {r['tablename'] for r in rows}
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return {r[0] for r in rows}


# ── Migration 008 ────────────────────────────────────────────────────────────

def test_config_whatsapp_no_schema(db):
    """init_db (rodou no import do app) criou config_whatsapp e aplicou a migration 8."""
    with db.get_conn() as conn:
        assert 'config_whatsapp' in _tabelas(conn)
        versoes = {r['version'] for r in conn.execute(
            "SELECT version FROM schema_migrations").fetchall()}
    assert 8 in versoes


@pytest.mark.sqlite_only
def test_runner_aplica_ate_008(tmp_path, db):
    """Banco novo aplica 1-10 e a 2ª passada é no-op."""
    conn = sqlite3.connect(str(tmp_path / 'fresh.db'))
    conn.row_factory = sqlite3.Row  # runner usa acesso por nome (r['version'])
    conn.isolation_level = None
    try:
        aplicadas = db.runner.apply_pending(conn, db.MIGRATIONS_DIR)
        assert aplicadas == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        assert 'config_whatsapp' in _tabelas(conn)
        assert db.runner.apply_pending(conn, db.MIGRATIONS_DIR) == []
    finally:
        conn.close()


@pytest.mark.sqlite_only
def test_migration_008_up_down(tmp_path, db):
    """A migration 008 cria e remove a tabela config_whatsapp."""
    mods = {m.version: m for m in db.runner.discover(db.MIGRATIONS_DIR)}
    m008 = mods[8]
    assert m008.name == 'add_config_whatsapp'

    conn = sqlite3.connect(str(tmp_path / 'm008.db'))
    try:
        m008.up(conn)
        assert 'config_whatsapp' in _tabelas(conn)
        cols = {r[1] for r in conn.execute(
            "PRAGMA table_info(config_whatsapp)").fetchall()}
        assert {'empresa', 'gdrive_folder_id', 'gdrive_credentials',
                'kommo_webhook_url', 'exportar_automatico'}.issubset(cols)

        m008.down(conn)
        assert 'config_whatsapp' not in _tabelas(conn)
    finally:
        conn.close()


# ── config_whatsapp: round-trip e segurança da credencial ────────────────────

def test_config_whatsapp_round_trip(db):
    """Salva e lê a config; a credencial vai para arquivo (não para o banco)."""
    empresa = 'INEPROTEC'
    db.salvar_config_whatsapp(
        empresa=empresa, folder_id='FOLDER_123',
        filename_template='cobrancas_{empresa}_{data}.xlsx',
        kommo_webhook_url='https://hook.make/abc', kommo_pipeline_id='42',
        exportar_automatico=False, credentials_json='{"type":"service_account"}',
    )
    cfg = db.get_config_whatsapp(empresa)
    assert cfg is not None
    assert cfg['gdrive_folder_id'] == 'FOLDER_123'
    assert cfg['kommo_webhook_url'] == 'https://hook.make/abc'
    assert cfg['exportar_automatico'] == 0
    assert cfg['tem_credenciais'] is True
    # A credencial nunca é devolvida em texto.
    assert 'gdrive_credentials' not in cfg
    # O JSON foi para o arquivo em secrets/, não para a coluna do banco.
    with db.get_conn() as conn:
        col = conn.execute(
            "SELECT gdrive_credentials FROM config_whatsapp WHERE empresa=?",
            (empresa,)).fetchone()['gdrive_credentials']
    assert col == db.GDRIVE_CRED_MARKER
    assert db.get_gdrive_credentials_path(empresa).read_text(encoding='utf-8') \
        == '{"type":"service_account"}'


def test_config_whatsapp_credencial_vazia_preserva(db):
    """Salvar com credentials_json vazio preserva a credencial anterior."""
    empresa = 'MATRICULAEAD'
    db.salvar_config_whatsapp(
        empresa=empresa, folder_id='F1', filename_template='x_{data}.xlsx',
        kommo_webhook_url='', kommo_pipeline_id='',
        exportar_automatico=True, credentials_json='{"k":"v1"}',
    )
    # Segundo save sem credencial — não deve apagar o arquivo existente.
    db.salvar_config_whatsapp(
        empresa=empresa, folder_id='F2', filename_template='y_{data}.xlsx',
        kommo_webhook_url='', kommo_pipeline_id='',
        exportar_automatico=True, credentials_json=None,
    )
    cfg = db.get_config_whatsapp(empresa)
    assert cfg['gdrive_folder_id'] == 'F2'
    assert cfg['tem_credenciais'] is True
    assert db.get_gdrive_credentials_path(empresa).read_text(encoding='utf-8') == '{"k":"v1"}'


def test_config_whatsapp_inexistente_retorna_none(db):
    assert db.get_config_whatsapp('EMPRESA_QUE_NAO_EXISTE') is None


# ── gdrive: degradação graciosa e lógica de upload ───────────────────────────

def test_gdrive_disponivel_retorna_bool():
    assert isinstance(gdrive.disponivel(), bool)


def test_gdrive_sem_libs_erro_claro(monkeypatch):
    """Sem as libs do Google, as operações retornam erro instrutivo (não quebram)."""
    monkeypatch.setattr(gdrive, '_GOOGLE_OK', False)
    ok, msg = gdrive.testar_conexao('qualquer.json', 'FOLDER')
    assert ok is False and 'pip install' in msg
    ok, msg = gdrive.upload_xlsx('c.json', 'F', 'arq.xlsx', 'r.xlsx')
    assert ok is False and 'pip install' in msg


def test_gdrive_testar_conexao_credencial_ausente(monkeypatch):
    """Com libs presentes mas credencial inexistente: erro claro, sem chamar a API."""
    monkeypatch.setattr(gdrive, '_GOOGLE_OK', True)
    ok, msg = gdrive.testar_conexao('caminho/inexistente.json', 'FOLDER')
    assert ok is False and 'não encontrada' in msg.lower()


def test_gdrive_upload_arquivo_local_ausente(monkeypatch):
    monkeypatch.setattr(gdrive, '_GOOGLE_OK', True)
    ok, msg = gdrive.upload_xlsx('c.json', 'F', 'nao/existe.xlsx', 'r.xlsx')
    assert ok is False and 'não encontrado' in msg.lower()


def test_gdrive_upload_cria_quando_nao_existe(monkeypatch, tmp_path):
    """Sem arquivo de mesmo nome na pasta, faz create (não update)."""
    chamadas = {'create': 0, 'update': 0}

    class _FakeFiles:
        def list(self, **kw):
            return _Exec({'files': []})

        def create(self, **kw):
            chamadas['create'] += 1
            return _Exec({'id': 'NEW', 'webViewLink': 'http://drive/NEW'})

        def update(self, **kw):
            chamadas['update'] += 1
            return _Exec({'id': 'UPD', 'webViewLink': 'http://drive/UPD'})

    class _Exec:
        def __init__(self, payload):
            self._p = payload

        def execute(self):
            return self._p

    class _FakeService:
        def files(self):
            return _FakeFiles()

    local = tmp_path / 'planilha.xlsx'
    local.write_text('conteudo', encoding='utf-8')

    monkeypatch.setattr(gdrive, '_GOOGLE_OK', True)
    monkeypatch.setattr(gdrive, '_MediaFileUpload', lambda *a, **k: object())
    monkeypatch.setattr(gdrive, '_build_service', lambda *a, **k: _FakeService())

    ok, link = gdrive.upload_xlsx('c.json', 'FOLDER', str(local), 'planilha.xlsx')
    assert ok is True
    assert link == 'http://drive/NEW'
    assert chamadas == {'create': 1, 'update': 0}


def test_gdrive_upload_substitui_quando_existe(monkeypatch, tmp_path):
    """Com arquivo de mesmo nome na pasta, faz update (substitui, não duplica)."""
    chamadas = {'create': 0, 'update': 0}

    class _Exec:
        def __init__(self, payload):
            self._p = payload

        def execute(self):
            return self._p

    class _FakeFiles:
        def list(self, **kw):
            return _Exec({'files': [{'id': 'OLD', 'name': 'planilha.xlsx'}]})

        def create(self, **kw):
            chamadas['create'] += 1
            return _Exec({'id': 'NEW', 'webViewLink': 'http://drive/NEW'})

        def update(self, **kw):
            chamadas['update'] += 1
            return _Exec({'id': 'OLD', 'webViewLink': 'http://drive/OLD'})

    class _FakeService:
        def files(self):
            return _FakeFiles()

    local = tmp_path / 'planilha.xlsx'
    local.write_text('conteudo', encoding='utf-8')

    monkeypatch.setattr(gdrive, '_GOOGLE_OK', True)
    monkeypatch.setattr(gdrive, '_MediaFileUpload', lambda *a, **k: object())
    monkeypatch.setattr(gdrive, '_build_service', lambda *a, **k: _FakeService())

    ok, link = gdrive.upload_xlsx('c.json', 'FOLDER', str(local), 'planilha.xlsx')
    assert ok is True
    assert link == 'http://drive/OLD'
    assert chamadas == {'create': 0, 'update': 1}


# ── Onda 2: rotas (configurar / testar / exportar) ───────────────────────────

def test_aba_whatsapp_em_configuracoes(client, users, login):
    """A aba WhatsApp aparece na página de Configurações."""
    login('admin', 'admin123')
    html = client.get('/configuracoes').get_data(as_text=True)
    assert 'tab-whatsapp' in html
    assert '/whatsapp/configurar' in html


def test_whatsapp_configurar_salva(client, db, users, login):
    """POST salva folder/template e grava a credencial fora do banco."""
    login('admin', 'admin123')
    data = {
        'gdrive_folder_id': 'FOLDER_ABC',
        'gdrive_filename_template': 'cob_{empresa}_{ddmmyyyy}.xlsx',
        'kommo_webhook_url': 'https://hook.make/x',
        'gdrive_credentials_file': (
            io.BytesIO(b'{"type":"service_account","private_key":"SECRET_TEST_KEY"}'),
            'sa.json'),
    }
    client.post('/whatsapp/configurar', data=data,
                content_type='multipart/form-data', follow_redirects=True)
    cfg = db.get_config_whatsapp('INEPROTEC')
    assert cfg['gdrive_folder_id'] == 'FOLDER_ABC'
    assert cfg['kommo_webhook_url'] == 'https://hook.make/x'
    assert cfg['tem_credenciais'] is True


def test_whatsapp_configurar_json_invalido(client, db, users, login):
    """Credencial que não é JSON válido é rejeitada com mensagem clara."""
    login('admin', 'admin123')
    data = {
        'gdrive_folder_id': 'F',
        'gdrive_credentials_file': (io.BytesIO(b'isto nao e json'), 'ruim.json'),
    }
    html = client.post('/whatsapp/configurar', data=data,
                       content_type='multipart/form-data',
                       follow_redirects=True).get_data(as_text=True)
    assert 'JSON válido' in html


def test_credencial_nunca_aparece_no_html(client, db, users, login):
    """AC: o conteúdo da credencial nunca é renderizado em Configurações."""
    login('admin', 'admin123')
    segredo = 'SUPER_SECRET_PRIVATE_KEY_42'
    data = {
        'gdrive_folder_id': 'F',
        'gdrive_credentials_file': (
            io.BytesIO(f'{{"type":"service_account","private_key":"{segredo}"}}'.encode()),
            'sa.json'),
    }
    client.post('/whatsapp/configurar', data=data,
                content_type='multipart/form-data', follow_redirects=True)
    html = client.get('/configuracoes').get_data(as_text=True)
    assert segredo not in html


def test_whatsapp_testar_sem_credencial(client, db, app, users, login, monkeypatch):
    """Sem credencial salva, /whatsapp/testar responde JSON ok=False (sem chamar API)."""
    monkeypatch.setattr(app.gdrive, 'disponivel', lambda: True)
    with db.get_conn() as conn:
        conn.execute("DELETE FROM config_whatsapp WHERE empresa='INEPROTEC'")
        conn.commit()
    cred = db.get_gdrive_credentials_path('INEPROTEC')
    if cred:
        cred.unlink()
    login('admin', 'admin123')
    resp = client.post('/whatsapp/testar')
    body = resp.get_json()
    assert body['ok'] is False
    assert 'credencial' in body['msg'].lower()


def test_whatsapp_exportar_sem_config_redireciona(client, db, users, login):
    """Sem Drive configurado, exportar avisa para configurar antes."""
    with db.get_conn() as conn:
        conn.execute("DELETE FROM config_whatsapp WHERE empresa='INEPROTEC'")
        conn.commit()
    cred = db.get_gdrive_credentials_path('INEPROTEC')
    if cred:
        cred.unlink()
    login('admin', 'admin123')
    html = client.post('/whatsapp/exportar', follow_redirects=True).get_data(as_text=True)
    assert 'Configure o Google Drive' in html


def test_whatsapp_exportar_registra_envios(client, db, app, users, login, monkeypatch, tmp_path):
    """Fluxo feliz: gera planilha, sobe no Drive e registra um envio por inadimplente."""
    empresa = 'INEPROTEC'
    db.salvar_config_whatsapp(
        empresa=empresa, folder_id='FOLDER_OK', filename_template='c_{ddmmyyyy}.xlsx',
        kommo_webhook_url='', kommo_pipeline_id='', exportar_automatico=False,
        credentials_json='{"type":"service_account"}',
    )
    with db.get_conn() as conn:
        conn.execute("DELETE FROM envios WHERE empresa=? AND canal='whatsapp_crm'", (empresa,))
        conn.commit()

    consolidado = pd.DataFrame([
        {'CPF': '12345678901', 'Dias_Atraso': 5},
        {'CPF': '98765432100', 'Dias_Atraso': 40},
    ])
    monkeypatch.setattr(app, '_carregar_estado', lambda emp: (consolidado, {}, None, {}))
    monkeypatch.setattr(app.proc, 'gerar_planilha_crm',
                        lambda *a, **k: tmp_path / 'planilha.xlsx')
    monkeypatch.setattr(app.gdrive, 'disponivel', lambda: True)
    monkeypatch.setattr(app.gdrive, 'upload_xlsx',
                        lambda *a, **k: (True, 'http://drive/OK'))

    login('admin', 'admin123')
    resp = client.post('/whatsapp/exportar')  # sem seguir redirect (não re-renderiza a tela)
    assert resp.status_code == 302
    assert '/envio-mensagens' in resp.headers['Location']
    envios = db.get_envios_hoje(empresa, 'whatsapp_crm')
    assert len(envios) == 2
