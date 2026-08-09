from decimal import Decimal


DAILY_MEAL_LIMIT = Decimal("6.50")


def calculate_meal_reimbursement(receipt_amount):
    amount = Decimal(str(receipt_amount))

    return min(amount, DAILY_MEAL_LIMIT)