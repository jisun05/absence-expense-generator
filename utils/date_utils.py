from datetime import date


def get_previous_month():
    today = date.today()

    if today.month == 1:
        return today.year - 1, 12

    return today.year, today.month - 1