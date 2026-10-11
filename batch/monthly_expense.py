from absence_io.auth import get_access_token
from absence_io.timespans import get_timespans
from expense.transformer import summarize_daily_work_times
from receipts.drive import get_receipt_files
from receipts.pdf_generator import create_receipt_pdf
from receipts.processor import process_receipts
from utils.date_utils import get_previous_month

# PostgreSQL 저장
# from database.repository import save_work_record
# from database.repository import save_receipt
# from database.repository import save_expense

from reports.excel_generator import create_expense_excel


def run_monthly_expense():

    year, month = get_previous_month()

    print(f"{year}-{month:02d} searching DATA")

    token = get_access_token()

    result = get_timespans(
        token=token,
        year=year,
        month=month,
    )

    daily_work_times = summarize_daily_work_times(
        result["data"]
    )

    # PostgreSQL에 근무 기록 저장
    #  DB 연결 시
    #
    # for work_day in daily_work_times:
    #     save_work_record(work_day)

    print("\nWork times:")

    for item in daily_work_times:
        print(
            item["date"],
            item["start"].strftime("%H:%M"),
            "->",
            item["end"].strftime("%H:%M"),
            f"({item['duration_text']})",
        )


    receipt_files = get_receipt_files()

    print(
        f"\nFound {len(receipt_files)} "
        "receipt files in Google Drive."
    )

    receipt_summary = process_receipts(
        receipt_files=receipt_files,
        daily_work_times=daily_work_times,
        year=year,
        month=month,
    )

    # PostgreSQL에 영수증 저장
    # DB 연결 시 주석 해제
    #
    # for receipt in receipt_summary["receipts"]:
    #     save_receipt(receipt)

    # PostgreSQL에 식대 청구 결과 저장
    # 나중에 DB 연결 시 주석 해제
    #
    # for receipt in receipt_summary["receipts"]:
    #     save_expense({
    #         "date": receipt["date"],
    #         "receipt_amount": receipt["receipt_amount"],
    #         "reimbursement": receipt["reimbursement"],
    #     })


    print("\nMeal expenses:")

    for item in receipt_summary["receipts"]:
        print(
            f"{item['date']} "
            f"receipt: €{item['receipt_amount']:.2f} "
            f"reimbursement: "
            f"€{item['reimbursement']:.2f}"
        )

    print(
        "\nTotal reimbursement: "
        f"€{receipt_summary['total_reimbursement']:.2f}"
    )


    receipt_files_for_pdf = [
        {
            "id": item["file_id"],
            "name": item["filename"],
        }
        for item in receipt_summary["receipts"]
    ]

    if receipt_files_for_pdf:
        create_receipt_pdf(
            receipt_files_for_pdf,
            f"output/receipts_{year}_{month:02d}.pdf",
        )

        print("\nReceipt PDF created successfully.")

    else:
        print(
            "\nNo eligible receipts found. "
            "PDF was not created."
        )

    create_expense_excel(
        year=year,
        month=month,
        daily_work_times=daily_work_times,
        receipts=receipt_summary["receipts"],
    )

    print("\nExpense Excel created successfully.")