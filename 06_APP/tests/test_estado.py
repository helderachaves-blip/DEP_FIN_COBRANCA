"""Testes do estado de consolidação em banco (EPIC-02 Onda 3 — matar o pickle).

Garante que o estado da sessão (DataFrames + stats) faz round-trip via blob no banco,
que substitui em vez de duplicar, que é isolado por empresa, que a limpeza funciona,
que a migração de categorias antigas continua valendo — e, principalmente, que NENHUM
arquivo .pkl é gravado em disco (pré-requisito para rodar stateless na nuvem).
"""
import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def _limpa_estado(db):
    """Cada teste começa sem estado para nenhuma empresa."""
    with db.get_conn() as conn:
        conn.execute("DELETE FROM estado_consolidacao")
        conn.commit()
    yield


def _consolidado(categoria='Novos Inadimplentes', dias=1):
    return pd.DataFrame({
        'Nome': ['João Silva', 'Maria Souza'],
        'CPF': ['00000000001', '00000000002'],
        'Dias_Atraso': [dias, dias],
        'Categoria': [categoria, categoria],
    })


def test_round_trip_preserva_frame_e_stats(app):
    consolidado = _consolidado()
    stats = {'total': 2, 'cat_novos': 2}
    avencer = pd.DataFrame({'Nome': ['Ana'], 'CPF': ['00000000003']})
    stats_avencer = {'total': 1}

    app._salvar_estado(consolidado, stats, 'INEPROTEC', avencer, stats_avencer)
    c, s, av, sa = app._carregar_estado('INEPROTEC')

    pd.testing.assert_frame_equal(c, consolidado)
    assert s == stats
    pd.testing.assert_frame_equal(av, avencer)
    assert sa == stats_avencer


def test_carregar_sem_estado_retorna_nones(app):
    assert app._carregar_estado('INEPROTEC') == (None, None, None, None)


def test_salvar_substitui_nao_duplica(app, db):
    app._salvar_estado(_consolidado(), {'total': 1}, 'INEPROTEC')
    app._salvar_estado(_consolidado(), {'total': 99}, 'INEPROTEC')

    with db.get_conn() as conn:
        n = conn.execute(
            "SELECT COUNT(*) FROM estado_consolidacao WHERE empresa = ?", ('INEPROTEC',)
        ).fetchone()[0]
    assert n == 1
    _, s, _, _ = app._carregar_estado('INEPROTEC')
    assert s == {'total': 99}


def test_estado_isolado_por_empresa(app):
    app._salvar_estado(_consolidado(), {'total': 1}, 'INEPROTEC')
    assert app._carregar_estado('MATRICULAEAD') == (None, None, None, None)
    assert app._carregar_estado('INEPROTEC')[0] is not None


def test_limpar_estado_remove(app, db):
    app._salvar_estado(_consolidado(), {'total': 1}, 'INEPROTEC')
    assert db.estado_existe('INEPROTEC') is True

    app._limpar_estado('INEPROTEC')
    assert db.estado_existe('INEPROTEC') is False
    assert app._carregar_estado('INEPROTEC') == (None, None, None, None)


def test_estado_existe_reflete_presenca(db, app):
    assert db.estado_existe('INEPROTEC') is False
    app._salvar_estado(_consolidado(), {'total': 1}, 'INEPROTEC')
    assert db.estado_existe('INEPROTEC') is True


def test_migracao_categorias_antigas(app):
    # 'Régua' (categoria antiga) deve virar 'Inadimplentes Mês' ao carregar.
    consolidado = _consolidado(categoria='Régua', dias=10)
    app._salvar_estado(consolidado, {'total': 2}, 'INEPROTEC')

    c, s, _, _ = app._carregar_estado('INEPROTEC')
    assert set(c['Categoria']) == {'Inadimplentes Mês'}
    assert s['cat_mes'] == 2


def test_nenhum_pkl_gravado_em_disco(app, db):
    app._salvar_estado(_consolidado(), {'total': 1}, 'INEPROTEC')
    pkls = list(db.DATA_DIR.rglob('*.pkl'))
    assert pkls == [], f"Estado não deveria gerar .pkl em disco: {pkls}"
