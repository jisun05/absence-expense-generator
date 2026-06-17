from datetime import datetime


def summarize_daily_work_times(timespans):
    daily = {}

    for item in timespans:
        if item.get("type") != "work":
            continue

        start = datetime.fromisoformat(item["startInTimezone"])
        end = datetime.fromisoformat(item["endInTimezone"])

        work_date = start.date()

        if work_date not in daily:
            daily[work_date] = {
                "date": work_date,
                "start": start,
                "end": end,
            }
        else:
            if start < daily[work_date]["start"]:
                daily[work_date]["start"] = start

            if end > daily[work_date]["end"]:
                daily[work_date]["end"] = end

    return sorted(daily.values(), key=lambda x: x["date"])