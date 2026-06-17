import os

import requests


def get_timespans(token, year=2026, month=5):
    url = "https://app.absence.io/api/v2/timespans"

    user_id = os.getenv("ABSENCE_USER_ID")

    start_date = f"{year}-{month:02d}-01T00:00:00.000Z"

    if month == 12:
        end_date = f"{year + 1}-01-01T00:00:00.000Z"
    else:
        end_date = f"{year}-{month + 1:02d}-01T00:00:00.000Z"

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "skip": 0,
            "limit": 100,
            "filter": {
                "userId": user_id,
                "start": {
                    "$gte": start_date,
                    "$lt": end_date,
                },
            },
        },
    )

    response.raise_for_status()

    return response.json()