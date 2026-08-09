import io
import os

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_drive_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )

            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
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