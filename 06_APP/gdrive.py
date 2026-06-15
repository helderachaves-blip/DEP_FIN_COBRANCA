"""
Upload de planilhas no Google Drive (STORY-H-01).

Sobe a planilha CRM gerada pelo app num Shared Drive do Google Workspace, usando uma
Service Account. No Shared Drive os arquivos pertencem à organização (não à SA), o que
evita o erro `storageQuotaExceeded` — por isso todas as chamadas usam
`supportsAllDrives=True`.

Design modular (CLI-First): a obtenção das credenciais fica isolada em
`_service_account_creds()`. Trocar para OAuth na v2 SaaS é só adicionar outro provedor
de credencial e selecionar pelo `auth_method` — o resto do upload não muda.

Os imports do Google são protegidos: se as libs ainda não estiverem instaladas, o app
continua subindo e `disponivel()` retorna False (a UI mostra instrução de instalação).
"""

from pathlib import Path

try:
    from google.oauth2 import service_account as _sa
    from googleapiclient.discovery import build as _build
    from googleapiclient.http import MediaFileUpload as _MediaFileUpload
    _GOOGLE_OK = True
    _IMPORT_ERR = None
except Exception as e:  # pragma: no cover - ambiente sem as libs Google
    _sa = _build = _MediaFileUpload = None
    _GOOGLE_OK = False
    _IMPORT_ERR = str(e)

# drive.file basta para Shared Drive: a SA enxerga/gerencia apenas os arquivos que ela
# própria criou — exatamente o que queremos para substituir a planilha do dia.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def disponivel() -> bool:
    """True se as dependências do Google estão instaladas."""
    return _GOOGLE_OK


def _erro_libs() -> str:
    return (
        "Bibliotecas do Google não instaladas. Rode: "
        "pip install -r requirements.txt"
        + (f" (detalhe: {_IMPORT_ERR})" if _IMPORT_ERR else "")
    )


def _service_account_creds(credentials_path: str | Path):
    """Credenciais a partir do JSON da Service Account (provedor 'service_account')."""
    return _sa.Credentials.from_service_account_file(
        str(credentials_path), scopes=SCOPES
    )


def _build_service(credentials_path: str | Path, auth_method: str = 'service_account'):
    """Constrói o cliente do Drive. Ponto de extensão para OAuth na v2."""
    if auth_method != 'service_account':
        raise ValueError(f"auth_method não suportado ainda: {auth_method}")
    creds = _service_account_creds(credentials_path)
    return _build('drive', 'v3', credentials=creds, cache_discovery=False)


def _buscar_arquivo(service, folder_id: str, nome: str) -> str | None:
    """ID de um arquivo de mesmo nome na pasta (para substituir), ou None."""
    q = (
        f"name = '{nome}' and '{folder_id}' in parents and trashed = false"
    )
    resp = service.files().list(
        q=q, spaces='drive', fields='files(id, name)',
        supportsAllDrives=True, includeItemsFromAllDrives=True,
    ).execute()
    arquivos = resp.get('files', [])
    return arquivos[0]['id'] if arquivos else None


def testar_conexao(credentials_path: str | Path, folder_id: str) -> tuple[bool, str]:
    """Valida credenciais + acesso à pasta. Retorna (ok, mensagem)."""
    if not _GOOGLE_OK:
        return False, _erro_libs()
    if not credentials_path or not Path(credentials_path).exists():
        return False, "Credencial da Service Account não encontrada."
    if not folder_id:
        return False, "Informe o ID da pasta de destino no Drive."
    try:
        service = _build_service(credentials_path)
        meta = service.files().get(
            fileId=folder_id, fields='id, name', supportsAllDrives=True,
        ).execute()
        return True, f"Conexão OK — pasta '{meta.get('name', folder_id)}' acessível."
    except Exception as e:
        return False, f"Falha ao acessar o Drive: {e}"


def upload_xlsx(credentials_path: str | Path, folder_id: str,
                local_path: str | Path, remote_filename: str,
                auth_method: str = 'service_account') -> tuple[bool, str]:
    """Sobe (ou substitui) o XLSX na pasta. Retorna (ok, link_ou_erro)."""
    if not _GOOGLE_OK:
        return False, _erro_libs()
    if not Path(local_path).exists():
        return False, f"Arquivo local não encontrado: {local_path}"
    try:
        service = _build_service(credentials_path, auth_method)
        media = _MediaFileUpload(str(local_path), mimetype=XLSX_MIME, resumable=False)
        existente = _buscar_arquivo(service, folder_id, remote_filename)
        if existente:
            arq = service.files().update(
                fileId=existente, media_body=media,
                fields='id, webViewLink', supportsAllDrives=True,
            ).execute()
        else:
            arq = service.files().create(
                body={'name': remote_filename, 'parents': [folder_id]},
                media_body=media, fields='id, webViewLink',
                supportsAllDrives=True,
            ).execute()
        return True, arq.get('webViewLink') or arq.get('id', '')
    except Exception as e:
        return False, f"Falha no upload: {e}"
