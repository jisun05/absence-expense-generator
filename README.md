# Absence Expense Generator

[English](README.md) | [한국어](README.ko.md)

A Python-based automation tool that processes company canteen receipts, validates meal reimbursement eligibility against work records, and generates monthly expense reports.

## Overview

Manually preparing monthly meal expense claims can be repetitive and error-prone.

This project automates the workflow by integrating attendance data, receipt images, OCR-based data extraction, and a PostgreSQL database.

## Features

- **Attendance Integration** — Retrieves work time records from the absence.io API.
- **Receipt Processing** — Downloads receipt images from Google Drive.
- **OCR Extraction** — Extracts receipt dates and transaction amounts using Tesseract OCR.
- **Eligibility Validation** — Includes receipts only when the receipt date matches a work record and the recorded work duration is at least 8 hours.
- **Expense Calculation** — Calculates reimbursement using the actual eligible receipt amount.
- **PDF Generation** — Generates a PDF containing eligible receipts in chronological order.
- **Database Persistence** — Stores work records, receipts, and expense data in PostgreSQL.
- **Automated Testing** — Uses pytest to validate core functionality.
- **Continuous Integration** — Uses GitHub Actions to run tests and validate Docker image builds.

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| OCR | Tesseract OCR, pytesseract |
| Image Processing | Pillow |
| Attendance API | absence.io API |
| File Storage | Google Drive API |
| Database | PostgreSQL |
| Testing | pytest |
| Containerization | Docker, Docker Compose |
| CI | GitHub Actions |

## Project Structure

```text
absence-expense-generator/
├── absence_io/       # absence.io API integration
├── batch/            # Monthly expense workflow
├── config/           # Application settings
├── database/         # Database connection, schema, and repository
├── expense/          # Expense calculation and report transformation
├── receipts/         # Receipt download, OCR, processing, and PDF generation
├── tests/             # Automated tests
├── utils/             # Utility functions
├── output/            # Generated reports
├── main.py            # Application entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── README.ko.md
```

## How It Works

1. Retrieve attendance records for the target month.
2. Summarize daily work times.
3. Retrieve receipt images from Google Drive.
4. Extract receipt dates and amounts using OCR.
5. Match receipt dates against work records.
6. Exclude receipts without matching work records, receipts outside the target month, and workdays with less than 8 hours of recorded work.
7. Save eligible work records, receipts, and expenses to PostgreSQL.
8. Generate a PDF report containing eligible receipts in chronological order.

## Requirements

- Python 3.12 or later
- Tesseract OCR
- PostgreSQL
- Google Drive API credentials
- absence.io API credentials

Docker and Docker Compose can be used to run the application in containers.

## Configuration

Configure the application using environment variables in a local `.env` file.

Use `.env.example` as a template if it contains the required settings.

Do not commit `.env`, `credentials.json`, or `token.json` to version control.

Google Drive API and absence.io API access must be configured before running the complete workflow.

## Run Locally

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ensure that Tesseract OCR and the required API credentials are configured.

Run the monthly expense workflow:

```bash
python main.py
```

## Run with Docker Compose

Start the database service:

```bash
docker compose up -d db
```

Check the service status:

```bash
docker compose ps
```

Configure the required environment variables and API credentials before running the complete application.

## Testing

Run the automated test suite:

```bash
python -m pytest -v
```

The test suite covers expense calculations, receipt parsing, receipt processing, database repository operations, and work-time transformations.

## Continuous Integration

GitHub Actions runs the following checks on pushes and pull requests targeting `main`:

- Python automated tests
- Docker image build validation

Workflow configuration:

`.github/workflows/ci.yml`

## Future Improvements

- Improve OCR date extraction for additional receipt formats.
- Add more robust error handling and structured logging.
- Expand automated tests for edge cases.
- Improve deployment and operational documentation.

## License

No license has been specified yet.