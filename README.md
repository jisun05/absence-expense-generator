# Absence Expense Generator

Automate monthly meal expense claims by combining work attendance records,
receipt processing, and expense report generation.

This project integrates the absence.io API, Google Drive, OCR, PostgreSQL,
and Excel/PDF generation to reduce manual work in monthly expense reporting.

[한국어 README](README.ko.md)

## Features

- **Attendance Integration**
  - Retrieve work time records from the absence.io API.
  - Summarize daily working hours.
  - Calculate elapsed working time from clock-in to clock-out.

- **Receipt Processing**
  - Retrieve receipt images from Google Drive.
  - Extract receipt amounts and dates using OCR.
  - Match receipts with attendance records by date.
  - Filter receipts according to expense eligibility rules.

- **Expense Calculation**
  - Calculate eligible meal reimbursements.
  - Include only eligible workdays with matching receipts.
  - Exclude workdays without receipts and receipts without eligible attendance.

- **Excel Report Generation**
  - Generate monthly expense reports using an Excel template.
  - Preserve the template's formatting and formulas.
  - Support up to 25 eligible workdays.
  - Calculate daily expenses and the final reimbursement amount.

- **PDF Generation**
  - Generate a PDF containing receipt images.
  - Organize receipts by date.

- **Database Integration**
  - Store work records, receipts, and expenses in PostgreSQL.

- **Automated Testing**
  - Test expense calculations, receipt parsing, data transformation,
    and database repository operations.

## Tech Stack

| Category | Technologies |
| --- | --- |
| Language | Python |
| API Integration | requests, absence.io API |
| Authentication | Google OAuth 2.0 |
| Cloud Storage | Google Drive API |
| OCR | Tesseract, pytesseract |
| Image Processing | Pillow |
| Excel | openpyxl |
| Database | PostgreSQL |
| Containerization | Docker, Docker Compose |
| Testing | pytest |

## Project Structure

```text
absence-expense-generator/
├── absence_io/       # absence.io API integration
├── batch/            # Monthly expense processing workflow
├── config/           # Application settings
├── database/         # Database connection and repositories
├── expense/          # Expense calculation and Excel generation
├── receipts/         # Receipt retrieval, OCR, parsing, and PDF generation
├── templates/        # Public example Excel template
├── tests/            # Automated tests
├── output/           # Generated reports
├── main.py           # Application entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── README.ko.md
```

## How It Works

```text
absence.io API
      |
      v
Retrieve Attendance Records
      |
      v
Summarize Daily Working Hours
      |
      +-------------------------+
                                |
Google Drive                    |
      |                         |
      v                         |
Retrieve Receipt Images         |
      |                         |
      v                         |
Extract Amounts and Dates       |
      |                         |
      +------------+------------+
                   |
                   v
        Match Attendance and Receipts
                   |
                   v
          Calculate Expenses
                   |
          +--------+--------+
          |                 |
          v                 v
      Excel Report      Receipt PDF
          |
          v
    Monthly Expense Claim
```

## Expense Eligibility Rules

A workday is eligible for meal reimbursement when:

1. The recorded working duration is at least 8 hours.
2. A receipt exists for the same date.
3. The receipt satisfies the project's eligibility rules.

The application excludes workdays without matching receipts and receipts
without eligible attendance records.

The reimbursement amount is based on the eligible receipt amount.

## Prerequisites

- Python 3.13.2
- Tesseract OCR
- PostgreSQL 16
- An absence.io API account and credentials
- A Google Cloud project with the Google Drive API enabled
- Docker Desktop and Docker Compose (if using Docker)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/jisun05/absence-expense-generator.git
cd absence-expense-generator
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a local `.env` file based on `.env.example`.

Add the required API credentials and database configuration.

Do not commit `.env` or any real credentials to GitHub.

### 5. Configure Google Drive Authentication

Configure Google OAuth credentials for the Google Drive API.

Place your local `credentials.json` in the location expected by the application.
Complete the OAuth authorization flow to generate `token.json` if required.

Both files contain sensitive authentication information and must remain private.

### 6. Configure Tesseract OCR

Install Tesseract OCR and ensure that it is available to the application.

On Windows, if Tesseract is installed in the default location, configure
`pytesseract` to use:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Adjust the path if Tesseract is installed elsewhere.

### 7. Start PostgreSQL

If using Docker Compose, review the database configuration and start the
required services:

```bash
docker compose up -d
```

Make sure the database configuration matches your local `.env` settings.

## Usage

After configuring the API credentials, Google Drive access, and database,
run the application:

```bash
python main.py
```

The application executes the monthly expense workflow, which retrieves
attendance records, processes receipts, calculates eligible expenses,
and generates reports.

Generated files are saved in the configured output directory.

## Excel Template

A sanitized example template is available in:

`templates/travel_expense_template_public.xlsx`

The public template is provided for demonstration purposes.

The original working template may contain company-specific information.
Keep private templates and confidential company data out of the public repository.

## Testing

Run the automated tests with:

```bash
python -m pytest -v
```

## Security

The following files must not be committed if they contain real credentials
or sensitive information:

- `.env`
- `credentials.json`
- `token.json`
- Private Excel templates
- Receipt images containing personal information
- Generated reports containing personal or financial data

Review `.gitignore` before committing changes.

## Future Improvements

- Improve OCR accuracy and error handling.
- Add more automated tests for the monthly reporting workflow.
- Improve configuration and setup validation.
- Expand report generation and data validation.

## License

This project is intended as a personal portfolio project.

Add a license file if you decide to distribute the code under a specific license.