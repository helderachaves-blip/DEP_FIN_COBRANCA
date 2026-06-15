"""008 - Tabela config_whatsapp (integracao WhatsApp via Google Drive + Kommo).

STORY-H-01. Configuracao por empresa para gerar a planilha CRM e subir no Google
Drive (Shared Drive via Service Account). As credenciais sensiveis NAO ficam aqui:
o JSON da Service Account e gravado em C:\\MATINE\\secrets\\gdrive_{empresa}.json e a
coluna `gdrive_credentials` carrega apenas o marcador `[file]` (espelha o padrao da
senha SMTP, que usa keyring). Ver database.py:salvar_config_whatsapp.
"""

version = 8
name = "add_config_whatsapp"


def up(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS config_whatsapp (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa                  TEXT NOT NULL UNIQUE,
            -- Google Drive
            gdrive_auth_method       TEXT NOT NULL DEFAULT 'service_account',
            gdrive_credentials       TEXT,            -- marcador '[file]' (JSON fica em secrets/)
            gdrive_folder_id         TEXT,            -- ID da pasta no Shared Drive
            gdrive_filename_template TEXT NOT NULL DEFAULT 'cobrancas_{empresa}_{data}.xlsx',
            -- Kommo
            kommo_webhook_url        TEXT,
            kommo_pipeline_id        TEXT,
            -- Comportamento
            exportar_automatico      INTEGER NOT NULL DEFAULT 0,  -- 0 = sob demanda
            -- Controle
            criado_em                TEXT NOT NULL DEFAULT (datetime('now')),
            atualizado_em            TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_config_whatsapp_empresa ON config_whatsapp(empresa)"
    )


def down(conn):
    conn.execute("DROP INDEX IF EXISTS idx_config_whatsapp_empresa")
    conn.execute("DROP TABLE IF EXISTS config_whatsapp")
