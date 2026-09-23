import pytest

from app.payroll.csv_import import CsvValidationError, parse_payroll_csv

VALID_CSV = (
    "employee_id,employee_name,annual_gross_salary,actual_net_salary\n"
    "emp-1,A. de Vries,50000,39140.33\n"
    "emp-2,B. Jansen,42000,39140.33\n"
).encode()


def test_parses_valid_csv():
    rows = parse_payroll_csv(VALID_CSV)
    assert len(rows) == 2
    assert rows[0]["employee_id"] == "emp-1"
    assert rows[0]["annual_gross_salary"] == 50000.0


def test_empty_file_raises():
    with pytest.raises(CsvValidationError):
        parse_payroll_csv(b"")


def test_missing_required_column_raises():
    bad_csv = b"employee_id,employee_name,annual_gross_salary\nemp-1,A,50000\n"
    with pytest.raises(CsvValidationError, match="actual_net_salary"):
        parse_payroll_csv(bad_csv)


def test_header_only_no_rows_raises():
    header_only = b"employee_id,employee_name,annual_gross_salary,actual_net_salary\n"
    with pytest.raises(CsvValidationError, match="no data rows"):
        parse_payroll_csv(header_only)


def test_non_numeric_salary_raises_with_line_number():
    bad_csv = (
        b"employee_id,employee_name,annual_gross_salary,actual_net_salary\n"
        b"emp-1,A. de Vries,fifty-thousand,39140.33\n"
    )
    with pytest.raises(CsvValidationError, match="Row 2"):
        parse_payroll_csv(bad_csv)


def test_tolerates_excel_bom():
    with_bom = b"\xef\xbb\xbf" + VALID_CSV
    rows = parse_payroll_csv(with_bom)
    assert len(rows) == 2
