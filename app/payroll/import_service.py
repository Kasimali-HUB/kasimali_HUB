"""
Turns a parsed CSV into real, queryable data: per-employee records (PII,
stays local), a persisted exception queue (pseudonymized, same as before),
and an updated PayrollSummary row so the dashboard reflects the import
immediately. Re-importing the same client/year/period replaces prior data
for that run rather than duplicating it.
"""

from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.countries.nl.payroll import PayslipInput, calculate_nl_payslip
from app.db.models import ExceptionRecord, PayrollRunEmployee, PayrollSummary
from app.exceptions.records import PayrollRunRecord
from app.exceptions.service import build_exception_queue


@dataclass
class ImportResult:
    headcount: int
    total_gross: float
    employer_cost: float
    flagged_count: int


async def import_payroll_run(
    db: AsyncSession,
    *,
    client_id: int,
    year: int,
    period: str,
    rows: list[dict],
    pseudonymization_secret: str,
) -> ImportResult:
    # Re-import is a replace, not an append - avoids silently doubling
    # headcount/gross if someone re-uploads a corrected file for the same period.
    await db.execute(
        delete(PayrollRunEmployee).where(
            PayrollRunEmployee.client_id == client_id,
            PayrollRunEmployee.year == year,
            PayrollRunEmployee.period == period,
        )
    )
    await db.execute(
        delete(ExceptionRecord).where(
            ExceptionRecord.client_id == client_id,
            ExceptionRecord.year == year,
            ExceptionRecord.period == period,
        )
    )

    db.add_all(
        [
            PayrollRunEmployee(
                client_id=client_id,
                year=year,
                period=period,
                employee_id=row["employee_id"],
                employee_name=row["employee_name"],
                annual_gross_salary=row["annual_gross_salary"],
                actual_net_salary=row["actual_net_salary"],
            )
            for row in rows
        ]
    )

    total_gross = sum(row["annual_gross_salary"] for row in rows)
    employer_cost = sum(
        calculate_nl_payslip(
            PayslipInput(annual_gross_salary=row["annual_gross_salary"])
        ).total_employer_cost
        for row in rows
    )
    headcount = len(rows)

    existing_summary = (
        await db.execute(
            select(PayrollSummary).where(
                PayrollSummary.client_id == client_id,
                PayrollSummary.year == year,
                PayrollSummary.period == period,
            )
        )
    ).scalar_one_or_none()

    if existing_summary is not None:
        existing_summary.headcount = headcount
        existing_summary.total_gross = total_gross
        existing_summary.employer_cost = employer_cost
    else:
        db.add(
            PayrollSummary(
                client_id=client_id,
                year=year,
                period=period,
                headcount=headcount,
                total_gross=total_gross,
                employer_cost=employer_cost,
            )
        )

    payroll_records = [
        PayrollRunRecord(
            employee_id=row["employee_id"],
            employee_name=row["employee_name"],
            annual_gross_salary=row["annual_gross_salary"],
            actual_net_salary=row["actual_net_salary"],
        )
        for row in rows
    ]
    payloads, _token_map = build_exception_queue(
        payroll_records,
        run_id=f"{client_id}-{year}-{period}",
        pseudonymization_secret=pseudonymization_secret,
    )
    db.add_all(
        [
            ExceptionRecord(
                client_id=client_id,
                year=year,
                period=period,
                employee_token=p.employee_token,
                annual_gross_salary=p.annual_gross_salary,
                expected_net_salary=p.expected_net_salary,
                actual_net_salary=p.actual_net_salary,
                variance_pct=p.variance_pct,
                flagged=p.flagged,
            )
            for p in payloads
        ]
    )

    await db.commit()

    return ImportResult(
        headcount=headcount,
        total_gross=total_gross,
        employer_cost=employer_cost,
        flagged_count=sum(1 for p in payloads if p.flagged),
    )
