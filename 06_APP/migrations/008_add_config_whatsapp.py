"""008 - Tabela config_whatsapp (integracao WhatsApp via Google Drive + Kommo).

STORY-H-01. Configuracao por empresa para gerar a planilha CRM e subir no Google
Drive (Shared Drive via Service Account). As credenciais sensiveis NAO ficam aqui:
o JSON da Service Account e gravado em C:\\MATINE\\secrets\\gdrive_{empresa}.json e a
coluna `gdrive_credentials` carrega apenas o marcador `[file]` (espelha o padrao da
senha SMTP, que usa keyring). Ver database.py:salvar_config_whatsapp.
"""
import ddl

version = 8
name = "add_config_whatsapp"


def up(conn):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS config_whatsapp (
            id                       {ddl.pk_int()},
            empresa                  TEXT NOT NULL UNIQUE,
            gdrive_auth_method       TEXT NOT NULL DEFAULT 'service_account',
            gdrive_credentials       TEXT,
            gdrive_folder_id         TEXT,
            gdrive_filename_template TEXT NOT NULL DEFAULT 'cobrancas_{{empresa}}_{{data}}.xlsx',
            kommo_webhook_url        TEXT,
            kommo_pipeline_id        TEXT,
            exportar_automatico      INTEGER NOT NULL DEFAULT 0,
            criado_em                TEXT NOT NULL {ddl.ts_default()},
            atualizado_em            TEXT NOT NULL {ddl.ts_default()}
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_config_whatsapp_empresa ON config_whatsapp(empresa)"
    )


def down(conn):
    conn.execute("DROP INDEX IF EXISTS idx_config_whatsapp_empresa")
    conn.execute("DROP TABLE IF EXISTS config_whatsapp")
