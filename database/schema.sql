CREATE TABLE IF NOT EXISTS work_records (
    id SERIAL PRIMARY KEY,
    work_date DATE NOT NULL UNIQUE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    total_minutes INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS receipts (
    id SERIAL PRIMARY KEY,
    receipt_date DATE NOT NULL UNIQUE,
    filename VARCHAR(255) NOT NULL,
    file_id VARCHAR(255) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    expense_date DATE NOT NULL UNIQUE,
    receipt_amount NUMERIC(10, 2) NOT NULL,
    reimbursement NUMERIC(10, 2) NOT NULL
);