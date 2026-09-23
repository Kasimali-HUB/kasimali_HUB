"""Parses the payroll import CSV into plain dicts, with clear errors on bad rows."""

import csv
import io

REQUIRED_COLUMNS = {"employee_id", "employee_name", "annual_gross_salary", "actual_net_salary"}


class CsvValidationError(ValueError):
    pass


def parse_payroll_csv(file_bytes: bytes) -> list[dict]:
    text = file_bytes.decode("utf-8-sig")  # tolerates a leading BOM from Excel exports
    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None:
        raise CsvValidationError("File is empty.")

    missing = REQUIRED_COLUMNS - set(reader.fieldnames)
    if missing:
        raise CsvValidationError(f"Missing required column(s): {', '.join(sorted(missing))}")

    rows = []
    for line_number, raw_row in enumerate(reader, start=2):  # header is line 1
        try:
            rows.append(
                {
                    "employee_id": raw_row["employee_id"].strip(),
                    "employee_name": raw_row["employee_name"].strip(),
                    "annual_gross_salary": float(raw_row["annual_gross_salary"]),
                    "actual_net_salary": float(raw_row["actual_net_salary"]),
                }
            )
        except (ValueError, KeyError) as exc:
            raise CsvValidationError(f"Row {line_number}: {exc}") from exc

    if not rows:
        raise CsvValidationError("File has a header but no data rows.")

    return rows
