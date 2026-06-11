"""Configuração de testes (pytest).

CRÍTICO: isola o ambiente do banco de PRODUÇÃO. Define `MATINE_DATA_DIR` para um
diretório temporário ANTES de qualquer import de `app`/`database`, de modo que
`DATA_DIR`/`DB_PATH` apontem para o temp. Os testes nunca tocam `C:\\MATINE`.

O conftest é carregado pelo pytest antes dos módulos de teste, então o env var
já está definido quando `app`/`database` forem importados pelos fixtures.
"""
import os
import shutil
import tempfile

# Deve rodar no import do conftest (antes de importar app/database).
_TEST_DIR = tempfile.mkdtemp(prefix='matine_test_')
os.environ['MATINE_DATA_DIR'] = _TEST_DIR

import pytest
from werkzeug.security import generate_password_hash


def pytest_unconfigure(config):
    """Remove o diretório temporário ao fim da sessão de testes."""
    shutil.rmtree(_TEST_DIR, ignore_errors=True)


def _hash(senha: str) -> str:
    return generate_password_hash(senha, method='pbkdf2:sha256')


@pytest.fixture(scope='session')
def app():
    """Módulo app já inicializado (setup_inicial rodou contra o banco temporário)."""
    import app as app_module
    app_module.app.config.update(TESTING=True)
    return app_module


@pytest.fixture()
def db(app):
    import database as database_module
    return database_module


@pytest.fixture()
def client(app):
    return app.app.test_client()


@pytest.fixture()
def users(db):
    """Reseta a tabela `usuarios` e cria um admin e um operador conhecidos.

    Torna cada teste determinístico e independente do seed do .env.
    Credenciais: admin/admin123 (admin) e oper/oper123 (operador).
    """
    with db.get_conn() as conn:
        conn.execute("DELETE FROM usuarios")
        conn.commit()
    db.criar_usuario('admin', 'Admin Teste', _hash('admin123'), True)
    db.criar_usuario('oper', 'Operador Teste', _hash('oper123'), False)
    return {'admin': ('admin', 'admin123'), 'oper': ('oper', 'oper123')}


@pytest.fixture()
def login(client):
    """Helper de login: login(usuario, senha) -> response."""
    def _login(usuario, senha):
        return client.post('/login',
                            data={'usuario': usuario, 'senha': senha},
                            follow_redirects=False)
    return _login
