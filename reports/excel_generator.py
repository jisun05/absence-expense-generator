from datetime import date, datetime, time, timedelta
from pathlib import Path
from copy import copy
from typing import Any

from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.worksheet.cell_range import CellRange


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = (
    PROJECT_ROOT / "templates" / "travel_expense_template.xlsx"
)
OUTPUT_DIR = PROJECT_ROOT / "output"

SHEET_NAME = "Reisekosten"

DATA_START_ROW = 8
ORIGINAL_DATA_CAPACITY = 14
ORIGINAL_TOTAL_ROW = 22
ORIGINAL_FINAL_AMOUNT_ROW = 25
MAX_WORK_DAYS = 25

DATE_COL = 1
LOCATION_COL = 2
START_TIME_COL = 3
END_TIME_COL = 4
HOURS_COL = 5
MEAL_COL = 14
DAILY_TOTAL_COL = 15


def normalize_date(value: Any) -> date | None:
    """Convert date, datetime, or supported string to date."""

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        value = value.strip()

        for fmt in (
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d.%m.%Y",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

    return None


def normalize_time(value: Any) -> time | None:
    """Convert supported values to time."""

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.time()

    if isinstance(value, time):
        return value

    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds()) % 86400

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return time(hours, minutes, seconds)

    if isinstance(value, str):
        value = value.strip()

        for fmt in (
            "%H:%M",
            "%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                continue

    return None


def normalize_money(value: Any) -> float:
    """Convert a value to a numeric amount."""

    if value is None:
        return 0.0

    if isinstance(value, str):
        value = value.strip().replace("€", "").replace(",", ".")

    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0.0


def get_first_value(
    record: dict,
    keys: tuple[str, ...],
) -> Any:
    """Return the first non-None value."""

    for key in keys:
        value = record.get(key)

        if value is not None:
            return value

    return None


def get_work_date(work_day: dict) -> date | None:
    """Get the date from a work record."""

    return normalize_date(work_day.get("date"))


def get_start_time(work_day: dict) -> time | None:
    """Get the start time from a work record."""

    value = get_first_value(
        work_day,
        (
            "start_time",
            "start",
            "from",
            "startTime",
            "time_start",
        ),
    )

    return normalize_time(value)


def get_end_time(work_day: dict) -> time | None:
    """Get the end time from a work record."""

    value = get_first_value(
        work_day,
        (
            "end_time",
            "end",
            "to",
            "endTime",
            "time_end",
        ),
    )

    return normalize_time(value)


def get_work_duration_days(work_day: dict) -> float:
    """
    Return elapsed time as a fraction of one day.

    Excel stores durations as fractions of a day.
    For example, 8 hours 30 minutes = 8.5 / 24.
    """

    start_time = get_start_time(work_day)
    end_time = get_end_time(work_day)

    if start_time is not None and end_time is not None:
        start_seconds = (
            start_time.hour * 3600
            + start_time.minute * 60
            + start_time.second
        )

        end_seconds = (
            end_time.hour * 3600
            + end_time.minute * 60
            + end_time.second
        )

        # Handle work that crosses midnight.
        if end_seconds < start_seconds:
            end_seconds += 24 * 3600

        elapsed_seconds = end_seconds - start_seconds

        return elapsed_seconds / 86400

    # Fallback: convert existing decimal hours to Excel duration.
    existing_hours = get_first_value(
        work_day,
        (
            "hours",
            "work_hours",
            "duration_hours",
            "total_hours",
        ),
    )

    if existing_hours is None:
        return 0.0

    return normalize_money(existing_hours) / 24


def get_receipt_date(receipt: dict) -> date | None:
    """Get the date from a receipt."""

    return normalize_date(receipt.get("date"))


def get_receipt_amount(receipt: dict) -> float:
    """Get the reimbursable amount from a receipt."""

    value = get_first_value(
        receipt,
        (
            "reimbursement",
            "amount",
            "total",
            "receipt_amount",
        ),
    )

    return normalize_money(value)


def build_receipts_by_date(
    receipts: list[dict],
) -> dict[date, dict]:
    """
    Index receipts by date.

    If multiple receipts have the same date, combine their amounts.
    """

    receipts_by_date: dict[date, dict] = {}

    for receipt in receipts:
        receipt_date = get_receipt_date(receipt)

        if receipt_date is None:
            continue

        amount = get_receipt_amount(receipt)

        if receipt_date not in receipts_by_date:
            receipts_by_date[receipt_date] = {
                **receipt,
                "date": receipt_date,
                "reimbursement": amount,
            }
        else:
            receipts_by_date[receipt_date]["reimbursement"] += amount

    return receipts_by_date


def set_cell_value(
    ws,
    row: int,
    col: int,
    value: Any,
) -> None:
    """Write to a cell, rejecting read-only merged cells."""

    cell = ws.cell(row=row, column=col)

    if isinstance(cell, MergedCell):
        raise ValueError(
            f"Cannot write to a merged cell: {cell.coordinate}"
        )

    cell.value = value


def copy_row_style(
    ws,
    source_row: int,
    target_row: int,
) -> None:
    """Copy formatting from one row to another."""

    for col in range(1, ws.max_column + 1):
        source = ws.cell(source_row, col)
        target = ws.cell(target_row, col)

        if source.has_style:
            target._style = copy(source._style)

        if source.number_format:
            target.number_format = source.number_format

        if source.alignment:
            target.alignment = copy(source.alignment)

        if source.protection:
            target.protection = copy(source.protection)

    ws.row_dimensions[target_row].height = (
        ws.row_dimensions[source_row].height
    )


def clear_data_area(
    ws,
    first_row: int,
    last_row: int,
) -> None:
    """Clear old values while preserving cell formatting."""

    for row in range(first_row, last_row + 1):
        for col in range(1, ws.max_column + 1):
            cell = ws.cell(row=row, column=col)

            if not isinstance(cell, MergedCell):
                cell.value = None


def move_footer(
    ws,
    extra_rows: int,
) -> None:
    """Move footer rows and their merged ranges down."""

    if extra_rows <= 0:
        return

    footer_merges = [
        str(merged_range)
        for merged_range in ws.merged_cells.ranges
        if CellRange(str(merged_range)).min_row
        >= ORIGINAL_TOTAL_ROW
    ]

    # Unmerge footer ranges before inserting rows.
    for merged_range in footer_merges:
        ws.unmerge_cells(merged_range)

    # Insert additional data rows.
    ws.insert_rows(
        ORIGINAL_TOTAL_ROW,
        amount=extra_rows,
    )

    # Restore merged ranges at their new positions.
    for merged_range in footer_merges:
        shifted_range = CellRange(merged_range)
        shifted_range.shift(row_shift=extra_rows)

        ws.merge_cells(str(shifted_range))


def write_summary(
    ws,
    total_row: int,
    last_data_row: int,
    final_amount_row: int,
) -> None:
    """Write the expense summary without total working hours."""

    # Summary label.
    set_cell_value(
        ws,
        total_row,
        5,
        "Gesamt EUR",
    )

    # Do not display total working hours.
    set_cell_value(
        ws,
        total_row,
        HOURS_COL,
        None,
    )

    # Calculate total meal expenses and daily totals.
    if last_data_row >= DATA_START_ROW:
        set_cell_value(
            ws,
            total_row,
            MEAL_COL,
            f"=SUM(N{DATA_START_ROW}:N{last_data_row})",
        )

        set_cell_value(
            ws,
            total_row,
            DAILY_TOTAL_COL,
            f"=SUM(O{DATA_START_ROW}:O{last_data_row})",
        )
    else:
        set_cell_value(
            ws,
            total_row,
            MEAL_COL,
            "=0",
        )

        set_cell_value(
            ws,
            total_row,
            DAILY_TOTAL_COL,
            "=0",
        )

    # Final reimbursement amount section.
    set_cell_value(
        ws,
        final_amount_row,
        10,
        "Summe/Sum",
    )

    set_cell_value(
        ws,
        final_amount_row,
        12,
        "(EUR)",
    )

    # Use total meal expenses as the final reimbursement amount.
    set_cell_value(
        ws,
        final_amount_row,
        14,
        f"=N{total_row}",
    )

    # Display the final amount as euros.
    ws.cell(
        row=final_amount_row,
        column=14,
    ).number_format = '#,##0.00 €'

    # Display the meal total as euros.
    ws.cell(
        row=total_row,
        column=MEAL_COL,
    ).number_format = '#,##0.00 €'

    ws.cell(
        row=total_row,
        column=DAILY_TOTAL_COL,
    ).number_format = '#,##0.00 €'


def create_expense_excel(
    year: int,
    month: int,
    daily_work_times: list[dict],
    receipts: list[dict],
) -> Path:
    """Generate the monthly expense Excel file."""

    # Check whether the Excel template exists.
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Excel template not found: {TEMPLATE_PATH}"
        )

    if not 1 <= month <= 12:
        raise ValueError(f"Invalid month: {month}")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR / f"expenses_{year}_{month:02d}.xlsx"
    )

    print(
        f"Generating expense Excel for "
        f"{year}-{month:02d}..."
    )

    # Index receipts by date.
    receipts_by_date = build_receipts_by_date(receipts)

    # Select work records for the requested month.
    monthly_work_times = []

    for work_day in daily_work_times:
        work_date = get_work_date(work_day)

        if work_date is None:
            continue

        if (
            work_date.year == year
            and work_date.month == month
        ):
            monthly_work_times.append(
                (work_date, work_day)
            )

    monthly_work_times.sort(
        key=lambda item: item[0]
    )

    # Include only work records with receipts on the same date.
    eligible_work_times = []

    for work_date, work_day in monthly_work_times:
        receipt = receipts_by_date.get(work_date)

        if receipt is not None:
            eligible_work_times.append(
                (work_date, work_day, receipt)
            )

    if len(eligible_work_times) > MAX_WORK_DAYS:
        raise ValueError(
            f"Eligible days exceed {MAX_WORK_DAYS}: "
            f"{len(eligible_work_times)}"
        )

    print(
        f"Eligible work days: "
        f"{len(eligible_work_times)}"
    )

    # Load the Excel template.
    workbook = load_workbook(TEMPLATE_PATH)

    try:
        if SHEET_NAME not in workbook.sheetnames:
            available_sheets = workbook.sheetnames

            raise ValueError(
                f"Worksheet '{SHEET_NAME}' not found. "
                f"Available sheets: {available_sheets}"
            )

        ws = workbook[SHEET_NAME]

        # Move footer when more than 14 data rows are needed.
        extra_rows = max(
            0,
            len(eligible_work_times)
            - ORIGINAL_DATA_CAPACITY,
        )

        if extra_rows:
            move_footer(
                ws,
                extra_rows,
            )

        total_row = ORIGINAL_TOTAL_ROW + extra_rows

        final_amount_row = (
            ORIGINAL_FINAL_AMOUNT_ROW + extra_rows
        )

        # Clear old data without removing cell formatting.
        last_clear_row = max(
            total_row - 1,
            DATA_START_ROW + MAX_WORK_DAYS - 1,
        )

        clear_data_area(
            ws,
            DATA_START_ROW,
            last_clear_row,
        )

        # Copy the template data-row formatting to additional rows.
        for index in range(len(eligible_work_times)):
            row = DATA_START_ROW + index

            if row != DATA_START_ROW:
                copy_row_style(
                    ws,
                    DATA_START_ROW,
                    row,
                )

        # Write work and receipt information.
        for index, (
            work_date,
            work_day,
            receipt,
        ) in enumerate(eligible_work_times):

            row = DATA_START_ROW + index

            # Date.
            set_cell_value(
                ws,
                row,
                DATE_COL,
                datetime.combine(
                    work_date,
                    time.min,
                ),
            )

            ws.cell(
                row=row,
                column=DATE_COL,
            ).number_format = "DD.MM.YYYY"

            # Location.
            set_cell_value(
                ws,
                row,
                LOCATION_COL,
                "Eschborn",
            )

            # Start time.
            start_time = get_start_time(work_day)

            if start_time is not None:
                set_cell_value(
                    ws,
                    row,
                    START_TIME_COL,
                    start_time,
                )

                ws.cell(
                    row=row,
                    column=START_TIME_COL,
                ).number_format = "HH:MM"

            # End time.
            end_time = get_end_time(work_day)

            if end_time is not None:
                set_cell_value(
                    ws,
                    row,
                    END_TIME_COL,
                    end_time,
                )

                ws.cell(
                    row=row,
                    column=END_TIME_COL,
                ).number_format = "HH:MM"

            # Working duration.
            duration = get_work_duration_days(work_day)

            set_cell_value(
                ws,
                row,
                HOURS_COL,
                duration,
            )

            ws.cell(
                row=row,
                column=HOURS_COL,
            ).number_format = "[h]:mm"

            # Meal reimbursement.
            meal_amount = get_receipt_amount(receipt)

            set_cell_value(
                ws,
                row,
                MEAL_COL,
                meal_amount,
            )

            ws.cell(
                row=row,
                column=MEAL_COL,
            ).number_format = '#,##0.00 €'

            # Daily total.
            # Apply this formula to every eligible data row.
            set_cell_value(
                ws,
                row,
                DAILY_TOTAL_COL,
                f"=F{row}+H{row}+J{row}+L{row}+N{row}",
            )

            ws.cell(
                row=row,
                column=DAILY_TOTAL_COL,
            ).number_format = '#,##0.00 €'

        # Calculate the last populated data row.
        # If there are no eligible days, this is one row before
        # the first data row.
        last_data_row = (
            DATA_START_ROW
            + len(eligible_work_times)
            - 1
        )

        # Write the summary and final reimbursement amount.
        write_summary(
            ws=ws,
            total_row=total_row,
            last_data_row=last_data_row,
            final_amount_row=final_amount_row,
        )

        # Ask Excel to recalculate formulas when opening the file.
        try:
            workbook.calculation.fullCalcOnLoad = True
            workbook.calculation.forceFullCalc = True
            workbook.calculation.calcMode = "auto"
        except AttributeError:
            pass

        # Save the completed workbook.
        workbook.save(output_path)

    finally:
        workbook.close()

    # Calculate the total meal expenses for the log.
    total_meal_amount = sum(
        get_receipt_amount(receipt)
        for _, _, receipt in eligible_work_times
    )

    print(f"Excel file created: {output_path}")
    print(
        f"Eligible work days: "
        f"{len(eligible_work_times)}"
    )
    print(
        f"Total meal expenses: "
        f"€{total_meal_amount:.2f}"
    )

    return output_path