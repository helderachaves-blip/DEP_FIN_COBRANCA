"""011 - Tabela config_sms (terceiro canal de comunicacao: SMS).

Sprint H-3. Configuracao por empresa para o canal SMS, provider-agnostic: os campos
sao genericos o suficiente para os providers candidatos (Twilio / Zenvia / Comtele
etc.) sem cravar um deles. O segredo (api_key/token) NAO fica aqui: e gravado em
DATA_DIR/secrets/sms_{empresa}.key (fora do git e do banco) e a coluna `api_key`
carrega apenas o marcador `[file]` — mesmo espirito da credencial do Drive
(config_whatsapp) e da senha SMTP (keyring). Na nuvem, o segredo vem da env var
SMS_{empresa}_API_KEY (Render). Ver database.py:salvar_config_sms.

A camada de ENVIO ainda nao esta implementada (provider TBD) — esta migration cria
apenas o scaffold de configuracao.
"""
import ddl

version = 11
name = "add_config_sms"


def up(conn):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS config_sms (
            id            {ddl.pk_int()},
            empresa       TEXT NOT NULL UNIQUE,
            provider      TEXT NOT NULL DEFAULT '',
            sender_id     TEXT,
            account_sid   TEXT,
            api_key       TEXT,
            endpoint      TEXT,
            ativo         INTEGER NOT NULL DEFAULT 0,
            criado_em     TEXT NOT NULL {ddl.ts_default()},
            atualizado_em TEXT NOT NULL {ddl.ts_default()}
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_config_sms_empresa ON config_sms(empresa)"
    )


def down(conn):
    conn.execute("DROP INDEX IF EXISTS idx_config_sms_empresa")
    conn.execute("DROP TABLE IF EXISTS config_sms")
