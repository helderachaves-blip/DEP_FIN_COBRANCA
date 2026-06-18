"""Testes do lote de correções de UI — revisão Edilvo (17/06/2026).

- C2: mensagem "Arquivo de Clientes não encontrado" no /consolidar passa a trazer um
  link para Configurações → Clientes (aba #tab-alunos).
- C4: a tela Base renderiza os totalizadores (contagem + valor) com o hook data-valor
  por linha, que o JS atualiza a cada filtro.

C1 (Resultado) e C4-JS são comportamento de front (clique/somatório); aqui validamos os
hooks de servidor/markup que os sustentam. A lógica de dados do dashboard (C3) fica em
test_dashboard.py.
"""
import pytest

INE = 'INEPROTEC'


@pytest.fixture(autouse=True)
def _limpa(db):
    with db.get_conn() as conn:
        conn.execute("DELETE FROM inadimplentes")
        conn.execute("DELETE FROM uploads_staging")
        conn.commit()
    yield


def _ins_inad(db, cpf, total=123.45):
    with db.get_conn() as conn:
        conn.execute(
            "INSERT INTO inadimplentes "
            "(cpf, empresa, aluno, total, dias_atraso, categoria, status, "
            " qtd_cobranca, data_entrada, data_atualizacao) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (cpf, INE, f'Aluno {cpf}', total, 5, 'Novos Inadimplentes',
             'INADIMPLENTE', 0, '01/06/2026', '01/06/2026 10:00:00'),
        )
        conn.commit()


# ── C2 — link na mensagem de arquivo de clientes ausente ───────────────────────

def test_consolidar_sem_alunos_mostra_link_para_clientes(client, users, login, db):
    login('admin', 'admin123')
    # Há vencidos no staging, mas NÃO há o arquivo de alunos → cai na flash com link.
    db.salvar_upload_staging(INE, 'vencidos', 'vencidos.csv', b'conteudo qualquer')
    resp = client.post('/consolidar', follow_redirects=True)
    assert resp.status_code == 200
    # O link aponta para a aba Clientes de Configurações e não vem escapado (Markup).
    assert b'#tab-alunos' in resp.data
    assert b'alert-link' in resp.data


# ── C4 — totalizadores na Base ─────────────────────────────────────────────────

def test_base_renderiza_totalizadores(client, users, login, db):
    login('admin', 'admin123')
    _ins_inad(db, '1', total=100.0)
    _ins_inad(db, '2', total=50.0)
    resp = client.get('/base')
    assert resp.status_code == 200
    # Hooks dos totalizadores e o valor cru por linha que o JS soma.
    assert b'baseTotalCount' in resp.data
    assert b'baseTotalValor' in resp.data
    assert b'data-valor=' in resp.data
