"""Testes do scaffold de SMS (Sprint H-3, terceiro canal de comunicação).

Cobre: migration 011 (up/down + runner), config_sms (round-trip com a chave de API
fora do banco), e as rotas (configurar / testar). O envio real é provider-agnostic e
ainda não está implementado — estes testes cobrem só a camada de configuração.
"""
import os
import sqlite3


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


# ── Migration 011 ────────────────────────────────────────────────────────────

def test_config_sms_no_schema(db):
    """init_db (rodou no import do app) criou config_sms e aplicou a migration 11."""
    with db.get_conn() as conn:
        assert 'config_sms' in _tabelas(conn)
        versoes = {r['version'] for r in conn.execute(
            "SELECT version FROM schema_migrations").fetchall()}
    assert 11 in versoes


def test_migration_011_up_down(tmp_path, db):
    """A migration 011 cria e remove a tabela config_sms."""
    import pytest
    if os.environ.get('TEST_DIALECT') == 'postgres':
        pytest.skip("up/down isolado roda só em SQLite")
    mods = {m.version: m for m in db.runner.discover(db.MIGRATIONS_DIR)}
    m011 = mods[11]
    assert m011.name == 'add_config_sms'

    conn = sqlite3.connect(str(tmp_path / 'm011.db'))
    try:
        m011.up(conn)
        assert 'config_sms' in _tabelas(conn)
        cols = {r[1] for r in conn.execute(
            "PRAGMA table_info(config_sms)").fetchall()}
        assert {'empresa', 'provider', 'sender_id', 'account_sid',
                'api_key', 'endpoint', 'ativo'}.issubset(cols)

        m011.down(conn)
        assert 'config_sms' not in _tabelas(conn)
    finally:
        conn.close()


# ── config_sms: round-trip e segurança da chave de API ───────────────────────

def test_config_sms_round_trip(db):
    """Salva e lê a config; a chave vai para arquivo (não para o banco)."""
    empresa = 'INEPROTEC'
    db.salvar_config_sms(
        empresa=empresa, provider='twilio', sender_id='MATINE',
        account_sid='AC123', endpoint='', ativo=True,
        api_key='SECRET_SMS_TOKEN',
    )
    cfg = db.get_config_sms(empresa)
    assert cfg is not None
    assert cfg['provider'] == 'twilio'
    assert cfg['sender_id'] == 'MATINE'
    assert cfg['account_sid'] == 'AC123'
    assert cfg['ativo'] == 1
    assert cfg['tem_api_key'] is True
    # A chave nunca é devolvida em texto.
    assert 'api_key' not in cfg
    # O segredo foi para o arquivo em secrets/, não para a coluna do banco.
    with db.get_conn() as conn:
        col = conn.execute(
            "SELECT api_key FROM config_sms WHERE empresa=?",
            (empresa,)).fetchone()['api_key']
    assert col == db.SMS_KEY_MARKER
    assert db.get_sms_api_key(empresa) == 'SECRET_SMS_TOKEN'


def test_config_sms_chave_vazia_preserva(db):
    """Salvar com api_key vazia preserva a chave anterior."""
    empresa = 'MATRICULAEAD'
    db.salvar_config_sms(
        empresa=empresa, provider='zenvia', sender_id='S1',
        account_sid='', endpoint='', ativo=True, api_key='TOKEN_V1',
    )
    # Segundo save sem chave — não deve apagar a existente.
    db.salvar_config_sms(
        empresa=empresa, provider='zenvia', sender_id='S2',
        account_sid='', endpoint='', ativo=False, api_key=None,
    )
    cfg = db.get_config_sms(empresa)
    assert cfg['sender_id'] == 'S2'
    assert cfg['ativo'] == 0
    assert cfg['tem_api_key'] is True
    assert db.get_sms_api_key(empresa) == 'TOKEN_V1'


def test_config_sms_inexistente_retorna_none(db):
    assert db.get_config_sms('EMPRESA_QUE_NAO_EXISTE') is None


def test_sms_api_key_env_override(db, monkeypatch):
    """Na nuvem a chave vem da env var SMS_{empresa}_API_KEY (precede o arquivo)."""
    monkeypatch.setenv('SMS_INEPROTEC_API_KEY', 'FROM_ENV')
    assert db.get_sms_api_key('INEPROTEC') == 'FROM_ENV'


# ── Rotas: aba, configurar, testar ───────────────────────────────────────────

def test_aba_sms_em_configuracoes(client, users, login):
    """A aba SMS aparece na página de Configurações."""
    login('admin', 'admin123')
    html = client.get('/configuracoes').get_data(as_text=True)
    assert 'tab-sms' in html
    assert '/sms/configurar' in html


def test_sms_configurar_salva(client, db, users, login):
    """POST salva provider/remetente e grava a chave fora do banco."""
    login('admin', 'admin123')
    data = {
        'provider': 'comtele',
        'sender_id': 'MATINE',
        'account_sid': '',
        'endpoint': '',
        'ativo': '1',
        'api_key': 'TOKEN_ROUTE',
    }
    client.post('/sms/configurar', data=data, follow_redirects=True)
    cfg = db.get_config_sms('INEPROTEC')
    assert cfg['provider'] == 'comtele'
    assert cfg['sender_id'] == 'MATINE'
    assert cfg['ativo'] == 1
    assert cfg['tem_api_key'] is True


def test_chave_sms_nunca_aparece_no_html(client, db, users, login):
    """A chave de API nunca é renderizada em Configurações."""
    login('admin', 'admin123')
    segredo = 'SUPER_SECRET_SMS_TOKEN_99'
    client.post('/sms/configurar', data={
        'provider': 'twilio', 'sender_id': 'X', 'account_sid': '',
        'endpoint': '', 'ativo': '1', 'api_key': segredo,
    }, follow_redirects=True)
    html = client.get('/configuracoes').get_data(as_text=True)
    assert segredo not in html


def test_sms_testar_sem_provider(client, db, users, login):
    """Sem provider configurado, /sms/testar responde JSON ok=False."""
    with db.get_conn() as conn:
        conn.execute("DELETE FROM config_sms WHERE empresa='INEPROTEC'")
        conn.commit()
    login('admin', 'admin123')
    body = client.post('/sms/testar').get_json()
    assert body['ok'] is False
    assert 'provider' in body['msg'].lower()


def test_sms_testar_config_valida(client, db, users, login):
    """Com provider + chave, /sms/testar responde ok=True (sem chamada externa)."""
    db.salvar_config_sms(
        empresa='INEPROTEC', provider='twilio', sender_id='M',
        account_sid='', endpoint='', ativo=True, api_key='TOKEN_OK',
    )
    login('admin', 'admin123')
    body = client.post('/sms/testar').get_json()
    assert body['ok'] is True
    assert 'twilio' in body['msg'].lower()
