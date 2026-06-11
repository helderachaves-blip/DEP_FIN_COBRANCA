"""Testes de Minha conta: edição do próprio nome e troca da própria senha."""


def _nome(db, usuario):
    return [u['nome'] for u in db.listar_usuarios() if u['usuario'] == usuario][0]


def test_editar_proprio_nome(client, db, users, login):
    login('oper', 'oper123')
    client.post('/conta/nome', data={'nome': 'Operador Renomeado'})
    assert _nome(db, 'oper') == 'Operador Renomeado'


def test_trocar_senha_atual_errada(client, users, login):
    login('oper', 'oper123')
    r = client.post('/conta/senha', data={
        'senha_atual': 'errada', 'senha_nova': 'novaSenha9', 'senha_conf': 'novaSenha9',
    }, follow_redirects=True)
    assert 'incorreta' in r.get_data(as_text=True)


def test_trocar_senha_curta(client, users, login):
    login('oper', 'oper123')
    r = client.post('/conta/senha', data={
        'senha_atual': 'oper123', 'senha_nova': '123', 'senha_conf': '123',
    }, follow_redirects=True)
    assert 'ao menos' in r.get_data(as_text=True)


def test_trocar_senha_confirmacao_diferente(client, users, login):
    login('oper', 'oper123')
    r = client.post('/conta/senha', data={
        'senha_atual': 'oper123', 'senha_nova': 'novaSenha9', 'senha_conf': 'outra9999',
    }, follow_redirects=True)
    assert 'confirmação' in r.get_data(as_text=True)


def test_trocar_senha_sucesso(client, users, login):
    login('oper', 'oper123')
    r = client.post('/conta/senha', data={
        'senha_atual': 'oper123', 'senha_nova': 'novaSenha9', 'senha_conf': 'novaSenha9',
    }, follow_redirects=True)
    assert 'sucesso' in r.get_data(as_text=True)
    client.get('/logout')
    r = client.post('/login', data={'usuario': 'oper', 'senha': 'novaSenha9'},
                    follow_redirects=False)
    assert r.status_code == 302 and r.headers['Location'].endswith('/')
