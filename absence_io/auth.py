import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_access_token():
    url = "https://app.absence.io/api/oauth/accesstoken"

    response = requests.post(
        url,
        data={
            "client_id": os.getenv("ABSENCE_CLIENT_ID"),
            "client_secret": os.getenv("ABSENCE_CLIENT_SECRET"),
            "grant_type": "client_credentials",
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )

    response.raise_for_status()

    return response.json()["access_token"]