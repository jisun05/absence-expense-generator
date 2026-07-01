from absence_io.auth import get_access_token
from absence_io.timespans import get_timespans
from utils.date_utils import get_previous_month
from expense.transformer import summarize_daily_work_times




def main():
    year, month = get_previous_month()

    print(f"{year}-{month:02d} searching DATA")
    token = get_access_token()
    result = get_timespans(token=token, year=year, month=month)

    daily_work_times = summarize_daily_work_times(result["data"])


    for item in daily_work_times:
        print(
            item["date"],
            item["start"].strftime("%H:%M"),
            "->",
            item["end"].strftime("%H:%M"),
            f'({item["hours"]}시간 {item["minutes"]}분)'
        )


if __name__ == "__main__":
    main()