"""Testes da gestão de usuários (admin) e das proteções anti-lockout."""


def _id(db, usuario):
    return [u['id'] for u in db.listar_usuarios() if u['usuario'] == usuario][0]


def test_admin_lista_usuarios(client, users, login):
    login('admin', 'admin123')
    r = client.get('/usuarios')
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert 'admin' in html and 'oper' in html


def test_operador_barrado(client, users, login):
    login('oper', 'oper123')
    r = client.get('/usuarios', follow_redirects=False)
    assert r.status_code == 302 and r.headers['Location'].endswith('/')


def test_criar_usuario(client, db, users, login):
    login('admin', 'admin123')
    client.post('/usuarios/criar',
                data={'usuario': 'novo', 'nome': 'Novo', 'senha': 'senha123'})
    assert any(u['usuario'] == 'novo' for u in db.listar_usuarios())


def test_criar_usuario_duplicado(client, users, login):
    login('admin', 'admin123')
    r = client.post('/usuarios/criar',
                    data={'usuario': 'admin', 'nome': 'X', 'senha': 'senha123'},
                    follow_redirects=True)
    assert 'Já existe' in r.get_data(as_text=True)


def test_criar_usuario_senha_curta(client, db, users, login):
    login('admin', 'admin123')
    antes = len(db.listar_usuarios())
    r = client.post('/usuarios/criar',
                    data={'usuario': 'curto', 'nome': 'X', 'senha': '123'},
                    follow_redirects=True)
    assert 'ao menos' in r.get_data(as_text=True)
    assert len(db.listar_usuarios()) == antes  # não criou


def test_resetar_senha(client, db, users, login):
    login('admin', 'admin123')
    oid = _id(db, 'oper')
    client.post(f'/usuarios/{oid}/senha', data={'senha': 'novaSenha9'})
    # operador agora loga com a nova senha
    c2 = client
    c2.get('/logout')
    r = c2.post('/login', data={'usuario': 'oper', 'senha': 'novaSenha9'},
                follow_redirects=False)
    assert r.status_code == 302 and r.headers['Location'].endswith('/')


def test_nao_remove_propria_conta(client, db, users, login):
    login('admin', 'admin123')
    aid = _id(db, 'admin')
    r = client.post(f'/usuarios/{aid}/remover', follow_redirects=True)
    assert 'própria conta' in r.get_data(as_text=True)
    assert any(u['usuario'] == 'admin' for u in db.listar_usuarios())


def test_nao_rebaixa_ultimo_admin(client, db, users, login):
    login('admin', 'admin123')
    aid = _id(db, 'admin')  # único admin
    r = client.post(f'/usuarios/{aid}/admin', data={'is_admin': '0'},
                    follow_redirects=True)
    assert 'último administrador' in r.get_data(as_text=True)
    assert db.get_usuario_por_id(aid)['is_admin'] == 1


def test_remover_usuario(client, db, users, login):
    login('admin', 'admin123')
    oid = _id(db, 'oper')
    client.post(f'/usuarios/{oid}/remover')
    assert not any(u['usuario'] == 'oper' for u in db.listar_usuarios())
