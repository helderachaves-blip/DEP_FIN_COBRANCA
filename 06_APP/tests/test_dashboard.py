"""Testes do Dashboard analítico (Sprint H-2, STORY-H-02).

Cobre a função de agregação `db.dashboard_stats` (KPIs, categorias, taxa de
quitação pós-cobrança, evolução semanal, recorte de envios por período) e a
rota `/dashboard` (login obrigatório + render). Datas em texto pt-BR são
agregadas em Python, então os testes valem para SQLite e Postgres.
"""
from datetime import datetime, timedelta

import pytest

INE = 'INEPROTEC'
MAT = 'MATRICULAEAD'


@pytest.fixture(autouse=True)
def _limpa(db):
    """Cada teste começa com as tabelas analíticas vazias."""
    with db.get_conn() as conn:
        conn.execute("DELETE FROM inadimplentes")
        conn.execute("DELETE FROM historico_atualizacoes")
        conn.execute("DELETE FROM envios")
        conn.commit()
    yield


def _ins_inad(db, empresa, cpf, status='INADIMPLENTE',
              categoria='Novos Inadimplentes', total=100.0, qtd_cobranca=0):
    with db.get_conn() as conn:
        conn.execute(
            "INSERT INTO inadimplentes "
            "(cpf, empresa, aluno, total, dias_atraso, categoria, status, "
            " qtd_cobranca, data_entrada, data_atualizacao) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (cpf, empresa, f'Aluno {cpf}', total, 5, categoria, status,
             qtd_cobranca, '01/06/2026', '01/06/2026 10:00:00'),
        )
        conn.commit()


def _ins_hist(db, empresa, data, total_base, novos=0, saidos=0):
    with db.get_conn() as conn:
        conn.execute(
            "INSERT INTO historico_atualizacoes "
            "(data, total_base, novos, saidos, continuam, empresa) VALUES (?,?,?,?,?,?)",
            (data, total_base, novos, saidos, 0, empresa),
        )
        conn.commit()


def _ins_envio(db, empresa, cpf, canal, data_envio):
    with db.get_conn() as conn:
        conn.execute(
            "INSERT INTO envios (cpf, empresa, canal, template_titulo, data_envio) "
            "VALUES (?,?,?,?,?)",
            (cpf, empresa, canal, None, data_envio),
        )
        conn.commit()


# ── _parse_dt_br ──────────────────────────────────────────────────────────────

def test_parse_dt_br_formatos(db):
    assert db._parse_dt_br('05/06/2026') == datetime(2026, 6, 5)
    assert db._parse_dt_br('05/06/2026 14:30:00') == datetime(2026, 6, 5, 14, 30)
    assert db._parse_dt_br('') is None
    assert db._parse_dt_br(None) is None
    assert db._parse_dt_br('lixo') is None


# ── Estado vazio ────────────────────────────────────────────────────────────

def test_stats_vazio(db):
    s = db.dashboard_stats(INE)
    assert s['tem_dados'] is False
    assert s['total_inadimplentes'] == 0
    assert s['valor_aberto'] == 0
    assert s['taxa_quitacao'] == 0.0
    assert s['evolucao'] == []
    assert s['categorias'] == []


# ── KPIs + categorias ─────────────────────────────────────────────────────────

def test_kpis_e_categorias(db):
    _ins_inad(db, INE, '1', categoria='Novos Inadimplentes', total=100)
    _ins_inad(db, INE, '2', categoria='Novos Inadimplentes', total=50)
    _ins_inad(db, INE, '3', categoria='Acima 30 Dias', total=300)
    _ins_inad(db, INE, '4', status='QUITADO', total=999)        # não conta no aberto
    _ins_inad(db, INE, '5', status='RENEGOCIADO', total=999)

    s = db.dashboard_stats(INE)
    assert s['tem_dados'] is True
    assert s['total_inadimplentes'] == 3
    assert s['valor_aberto'] == 450.0          # 100+50+300 (só INADIMPLENTE)
    assert s['quitados'] == 1
    assert s['renegociados'] == 1

    cats = {c['categoria']: c for c in s['categorias']}
    assert cats['Novos Inadimplentes']['qtd'] == 2
    assert cats['Novos Inadimplentes']['valor'] == 150.0
    assert cats['Acima 30 Dias']['qtd'] == 1
    assert 'QUITADO' not in cats   # categorias só listam inadimplentes ativos


# ── Valores totais, renegociação e cancelados (correção C3) ─────────────────────

def test_valores_renegociacao_cancelados(db):
    _ins_inad(db, INE, '1', status='INADIMPLENTE', total=100)
    _ins_inad(db, INE, '2', status='RENEGOCIADO',  total=200)
    _ins_inad(db, INE, '3', status='CANCELADO',    total=300)
    _ins_inad(db, INE, '4', status='QUITADO',      total=400)

    s = db.dashboard_stats(INE)
    assert s['valor_aberto'] == 100.0                 # só INADIMPLENTE
    assert s['renegociados'] == 1 and s['valor_renegociados'] == 200.0
    assert s['cancelados'] == 1 and s['valor_cancelados'] == 300.0
    assert s['quitados'] == 1
    assert s['valor_total'] == 1000.0                 # 100+200+300+400 (todos os status)


# ── Taxa de quitação pós-cobrança ──────────────────────────────────────────────

def test_taxa_quitacao(db):
    # 4 CPFs cobrados; 1 ainda inadimplente, 3 quitados → 75%
    _ins_inad(db, INE, '1', status='INADIMPLENTE', qtd_cobranca=2)
    _ins_inad(db, INE, '2', status='QUITADO', qtd_cobranca=1)
    _ins_inad(db, INE, '3', status='QUITADO', qtd_cobranca=3)
    _ins_inad(db, INE, '4', status='QUITADO', qtd_cobranca=1)
    # CPF nunca cobrado não entra no denominador
    _ins_inad(db, INE, '5', status='QUITADO', qtd_cobranca=0)

    s = db.dashboard_stats(INE)
    assert s['cobrados'] == 4
    assert s['quitados_cobrados'] == 3
    assert s['taxa_quitacao'] == 75.0


def test_taxa_quitacao_sem_cobrados_nao_divide_por_zero(db):
    _ins_inad(db, INE, '1', qtd_cobranca=0)
    s = db.dashboard_stats(INE)
    assert s['cobrados'] == 0
    assert s['taxa_quitacao'] == 0.0


# ── Evolução semanal (bucketização ISO) ────────────────────────────────────────

def test_evolucao_agrega_por_semana(db):
    # Duas entradas na MESMA semana ISO (01 e 03/06/2026) + uma em outra semana (15/06)
    _ins_hist(db, INE, '01/06/2026 09:00:00', total_base=100, novos=10, saidos=2)
    _ins_hist(db, INE, '03/06/2026 09:00:00', total_base=105, novos=5, saidos=1)
    _ins_hist(db, INE, '15/06/2026 09:00:00', total_base=120, novos=20, saidos=3)

    s = db.dashboard_stats(INE)
    evo = s['evolucao']
    assert len(evo) == 2                      # duas semanas
    # 1ª semana: soma novos (10+5) e saídos (2+1); total_base = último da semana (105)
    assert evo[0]['novos'] == 15
    assert evo[0]['saidos'] == 3
    assert evo[0]['total_base'] == 105
    # 2ª semana
    assert evo[1]['total_base'] == 120
    assert evo[1]['novos'] == 20


# ── Envios: total vs período ────────────────────────────────────────────────

def test_envios_periodo_e_canal(db):
    hoje = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    antigo = (datetime.now() - timedelta(days=60)).strftime('%d/%m/%Y %H:%M:%S')
    _ins_envio(db, INE, '1', 'whatsapp_crm', hoje)
    _ins_envio(db, INE, '2', 'email', hoje)
    _ins_envio(db, INE, '3', 'email', antigo)   # fora da janela de 30 dias

    s = db.dashboard_stats(INE, dias=30)
    assert s['envios_total'] == 3
    assert s['envios_periodo'] == 2
    assert s['envios_por_canal']['email'] == 2
    assert s['envios_por_canal']['whatsapp_crm'] == 1


# ── Isolamento por empresa ────────────────────────────────────────────────────

def test_isolamento_por_empresa(db):
    _ins_inad(db, INE, '1', total=100)
    _ins_inad(db, MAT, '1', total=500)   # mesmo cpf, empresa diferente

    s_ine = db.dashboard_stats(INE)
    s_mat = db.dashboard_stats(MAT)
    assert s_ine['total_inadimplentes'] == 1
    assert s_ine['valor_aberto'] == 100.0
    assert s_mat['valor_aberto'] == 500.0


# ── Rota /dashboard ───────────────────────────────────────────────────────────

def test_dashboard_exige_login(client):
    resp = client.get('/dashboard', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_dashboard_logado_renderiza(client, users, login):
    login('admin', 'admin123')
    resp = client.get('/dashboard')
    assert resp.status_code == 200
    assert b'Dashboard' in resp.data


def test_dashboard_mostra_estado_vazio(client, users, login):
    login('admin', 'admin123')
    resp = client.get('/dashboard')
    assert 'Ainda não há dados'.encode('utf-8') in resp.data
