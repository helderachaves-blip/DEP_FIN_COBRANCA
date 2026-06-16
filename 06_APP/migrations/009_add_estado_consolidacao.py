"""009 - Tabela estado_consolidacao (EPIC-02 Onda 3 - matar o pickle em disco).

O estado da sessao de consolidacao (DataFrames consolidado/avencer + stats) era
gravado em pickle no disco (`C:\\MATINE\\estado\\estado_{empresa}.pkl`), um acoplamento
por-processo/por-maquina que impede o app de rodar stateless na nuvem. Passa a ser um
blob versionado por empresa nesta tabela.

A coluna `payload` guarda o mesmo `pickle.dumps(dict)` de antes (zero perda de dtype).
PK = empresa (1 estado por empresa). Cross-dialect: BLOB no SQLite vira BYTEA no
Postgres (ddl.blob()); `ON CONFLICT(empresa)` suportado em ambos.
"""
import ddl

version = 9
name = "add_estado_consolidacao"


def up(conn):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS estado_consolidacao (
            empresa       TEXT NOT NULL PRIMARY KEY,
            payload       {ddl.blob()} NOT NULL,
            atualizado_em TEXT NOT NULL {ddl.ts_default()}
        )
        """
    )


def down(conn):
    conn.execute("DROP TABLE IF EXISTS estado_consolidacao")
