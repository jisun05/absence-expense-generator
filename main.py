from absence_io.auth import get_access_token
from absence_io.timespans import get_timespans
from utils.date_utils import get_previous_month

year, month = get_previous_month()

print(f"{year}-{month:02d} searching DATA")


def main():
    token = get_access_token()
    result = get_timespans(token, year=year, month=month)

    print(f"조회건수: {result.get('count')}")

    for item in result.get("data", []):
        print(
            item.get("startInTimezone"),
            "->",
            item.get("endInTimezone"),
            item.get("type"),
        )


if __name__ == "__main__":
    main()