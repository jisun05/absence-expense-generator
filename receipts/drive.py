import io
import os
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import json

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

TOKEN_FILE = "token.json"


def get_drive_service():
    creds = None
    token_json = os.getenv("GOOGLE_TOKEN_JSON")

    if token_json:
        creds = Credentials.from_authorized_user_info(
            json.loads(token_json),
            SCOPES,
        )
    elif os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if not creds:
        raise RuntimeError(
            "Google OAuth token is not configured."
        )

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError(
                "Google OAuth token is invalid or cannot be refreshed."
            )

    if not token_json:
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build(
        "drive",
        "v3",
        credentials=creds,
    )


def get_receipt_files():
    folder_id = os.getenv("GOOGLE_DRIVE_RECEIPT_FOLDER_ID")

    if not folder_id:
        raise ValueError(
            "GOOGLE_DRIVE_RECEIPT_FOLDER_ID is not set"
        )

    service = get_drive_service()

    query = (
        f"'{folder_id}' in parents "
        "and trashed = false "
        "and mimeType = 'image/jpeg'"
    )

    response = service.files().list(
        q=query,
        fields="files(id, name)",
        pageSize=100,
    ).execute()

    files = response.get("files", [])

    files.sort(key=_get_day_from_filename)

    return files


def _get_day_from_filename(file):
    filename = file["name"]

    filename_without_extension = os.path.splitext(
        filename
    )[0]

    return int(filename_without_extension)


def download_receipt(file_id):
    service = get_drive_service()

    request = service.files().get_media(
        fileId=file_id
    )

    buffer = io.BytesIO()

    downloader = MediaIoBaseDownload(
        buffer,
        request,
    )

    done = False

    while not done:
        _, done = downloader.next_chunk()

    buffer.seek(0)

    return buffer