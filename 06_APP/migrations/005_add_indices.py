"""005 - Indices de performance (DB-A02, DB-A03)."""

version = 5
name = "add_indices"


def up(conn):
    conn.execute("CREATE INDEX IF NOT EXISTS idx_inadimplentes_empresa ON inadimplentes(empresa)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_templates_empresa ON templates(empresa)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_envios_empresa_data ON envios(empresa, data_envio)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_historico_empresa ON historico_atualizacoes(empresa)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_config_email_empresa ON config_email(empresa)")


def down(conn):
    conn.execute("DROP INDEX IF EXISTS idx_inadimplentes_empresa")
    conn.execute("DROP INDEX IF EXISTS idx_templates_empresa")
    conn.execute("DROP INDEX IF EXISTS idx_envios_empresa_data")
    conn.execute("DROP INDEX IF EXISTS idx_historico_empresa")
    conn.execute("DROP INDEX IF EXISTS idx_config_email_empresa")
