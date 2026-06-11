"""Testes de autenticação: login, guard de rotas, logout, open-redirect."""


def test_rota_protegida_redireciona(client):
    r = client.get('/', follow_redirects=False)
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_pagina_login_acessivel(client):
    assert client.get('/login').status_code == 200


def test_login_credenciais_erradas(client, users):
    r = client.post('/login', data={'usuario': 'admin', 'senha': 'errada'})
    assert r.status_code == 200
    assert 'incorretos' in r.get_data(as_text=True)


def test_login_sucesso_e_acesso(client, users, login):
    r = login('admin', 'admin123')
    assert r.status_code == 302
    assert client.get('/').status_code == 200


def test_logout_encerra_sessao(client, users, login):
    login('admin', 'admin123')
    r = client.get('/logout', follow_redirects=False)
    assert r.status_code == 302 and '/login' in r.headers['Location']
    # após logout, rota protegida volta a redirecionar
    r = client.get('/base', follow_redirects=False)
    assert r.status_code == 302 and '/login' in r.headers['Location']


def test_static_publico_sem_login(client):
    r = client.get('/static/logo-ineprotec.png', follow_redirects=False)
    assert r.status_code != 302  # não redireciona para login


def test_open_redirect_bloqueado(client, users):
    r = client.post('/login?next=//evil.com',
                    data={'usuario': 'admin', 'senha': 'admin123'},
                    follow_redirects=False)
    assert r.headers['Location'].endswith('/')   # caiu no index, não em //evil.com


def test_next_interno_preservado(client, users):
    r = client.post('/login?next=/base',
                    data={'usuario': 'admin', 'senha': 'admin123'},
                    follow_redirects=False)
    assert r.headers['Location'].endswith('/base')
