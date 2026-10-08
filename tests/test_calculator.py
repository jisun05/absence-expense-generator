from decimal import Decimal

from expense.calculator import calculate_meal_reimbursement


def test_meal_reimbursement_with_string():
    result = calculate_meal_reimbursement("7.80")

    assert result == Decimal("7.80")


def test_meal_reimbursement_with_number():
    result = calculate_meal_reimbursement(7.80)

    assert result == Decimal("7.80")