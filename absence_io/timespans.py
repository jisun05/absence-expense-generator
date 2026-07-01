import os
from datetime import datetime
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


def calculate_work_time(timespans):
    """
    하루별 첫 출근 ~ 마지막 퇴근 시간 계산

    return:
    {
        "2026-05-01": {
            "minutes": 555,
            "hours": 9,
            "remaining_minutes": 15
        },
        ...
    }
    """

    result = {}

    for span in timespans:
        start = datetime.fromisoformat(
            span["start"].replace("Z", "+00:00")
        )
        end = datetime.fromisoformat(
            span["end"].replace("Z", "+00:00")
        )

        day = start.date().isoformat()

        if day not in result:
            result[day] = {
                "first": start,
                "last": end,
            }
        else:
            if start < result[day]["first"]:
                result[day]["first"] = start

            if end > result[day]["last"]:
                result[day]["last"] = end

    worked = {}

    for day, value in result.items():
        minutes = int((value["last"] - value["first"]).total_seconds() // 60)

        worked[day] = {
            "minutes": minutes,
            "hours": minutes // 60,
            "remaining_minutes": minutes % 60,
        }

    return worked