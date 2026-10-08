from datetime import date

from expense.transformer import summarize_daily_work_times


def test_summarize_daily_work_times():
    timespans = [
        {
            "type": "work",
            "startInTimezone": "2026-09-01T09:00:00",
            "endInTimezone": "2026-09-01T12:00:00",
        },
        {
            "type": "work",
            "startInTimezone": "2026-09-01T13:00:00",
            "endInTimezone": "2026-09-01T18:00:00",
        },
    ]

    result = summarize_daily_work_times(timespans)

    assert len(result) == 1
    assert result[0]["date"] == date(2026, 9, 1)
    assert result[0]["start"].hour == 9
    assert result[0]["end"].hour == 18
    assert result[0]["hours"] == 9
    assert result[0]["minutes"] == 0
    assert result[0]["total_minutes"] == 540


def test_ignore_non_work_timespans():
    timespans = [
        {
            "type": "break",
            "startInTimezone": "2026-09-01T12:00:00",
            "endInTimezone": "2026-09-01T13:00:00",
        },
        {
            "type": "work",
            "startInTimezone": "2026-09-01T09:00:00",
            "endInTimezone": "2026-09-01T17:00:00",
        },
    ]

    result = summarize_daily_work_times(timespans)

    assert len(result) == 1
    assert result[0]["hours"] == 8



def test_sort_by_date():
    timespans = [
        {
            "type": "work",
            "startInTimezone": "2026-09-03T09:00:00",
            "endInTimezone": "2026-09-03T17:00:00",
        },
        {
            "type": "work",
            "startInTimezone": "2026-09-01T09:00:00",
            "endInTimezone": "2026-09-01T17:00:00",
        },
    ]

    result = summarize_daily_work_times(timespans)

    assert result[0]["date"] == date(2026, 9, 1)
    assert result[1]["date"] == date(2026, 9, 3)
