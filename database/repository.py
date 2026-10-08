from database.connection import get_connection


def save_work_record(work_day):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO work_records (
                    work_date,
                    start_time,
                    end_time,
                    total_minutes
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (work_date)
                DO UPDATE SET
                    start_time = EXCLUDED.start_time,
                    end_time = EXCLUDED.end_time,
                    total_minutes = EXCLUDED.total_minutes
                """,
                (
                    work_day["date"],
                    work_day["start"].time(),
                    work_day["end"].time(),
                    work_day["total_minutes"],
                ),
            )

        conn.commit()


def save_receipt(receipt):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO receipts (
                    receipt_date,
                    filename,
                    file_id,
                    amount
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (receipt_date)
                DO UPDATE SET
                    filename = EXCLUDED.filename,
                    file_id = EXCLUDED.file_id,
                    amount = EXCLUDED.amount
                """,
                (
                    receipt["date"],
                    receipt["filename"],
                    receipt["file_id"],
                    receipt["receipt_amount"],
                ),
            )

        conn.commit()

def save_expense(expense):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO expenses (
                    expense_date,
                    receipt_amount,
                    reimbursement
                )
                VALUES (%s, %s, %s)
                ON CONFLICT (expense_date)
                DO UPDATE SET
                    receipt_amount = EXCLUDED.receipt_amount,
                    reimbursement = EXCLUDED.reimbursement
                """,
                (
                    expense["date"],
                    expense["receipt_amount"],
                    expense["reimbursement"],
                ),
            )

        conn.commit()