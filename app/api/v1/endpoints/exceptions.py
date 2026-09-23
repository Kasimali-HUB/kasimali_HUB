"""
Exposes Phase 3's build_exception_queue() over HTTP.

The employee records here are hardcoded demo data, not a real payroll run
pulled from a database - that wiring (a real PayrollRunRecord source tied
to an actual run) is still open, same as the dashboard's client onboarding.
What IS real: the request goes through the same pseudonymization and
gross-to-net comparison logic Phase 3 built and tested, so this endpoint
demonstrates the actual privacy boundary, not a mocked version of it.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import ExceptionRecord
from app.db.session import get_db
from app.exceptions.records import PayrollRunRecord
from app.exceptions.schemas import ExceptionPayload
from app.exceptions.service import build_exception_queue

router = APIRouter()
settings = get_settings()

_DEMO_RECORDS = [
    PayrollRunRecord("emp-1", "A. de Vries", 50_000, 39_140.33),  # matches engine
    PayrollRunRecord("emp-2", "B. Jansen", 42_000, 39_140.33),  # forced mismatch
    PayrollRunRecord("emp-3", "C. Bakker", 65_000, 47_000.00),  # forced mismatch
    PayrollRunRecord("emp-4", "D. Visser", 38_000, 30_500.00),  # close, within tolerance
]


@router.get("/exceptions/demo", response_model=list[ExceptionPayload], tags=["exceptions"])
async def demo_exception_queue() -> list[ExceptionPayload]:
    payloads, _token_map = build_exception_queue(
        _DEMO_RECORDS,
        run_id="demo-run-2026-03",
        pseudonymization_secret=settings.pseudonymization_secret,
    )
    # Note: _token_map (token -> real employee_id) is intentionally not
    # returned here - that lookup belongs on an authenticated, local-only
    # endpoint once real records exist, never in a payload shape like this.
    return payloads


@router.get("/exceptions", response_model=list[ExceptionPayload], tags=["exceptions"])
async def exception_queue_for_run(
    client_id: int,
    year: int,
    period: str,
    db: AsyncSession = Depends(get_db),
) -> list[ExceptionPayload]:
    """Real exceptions for an imported run - what Exception Review uses once
    something has actually been imported, as opposed to /exceptions/demo."""
    result = await db.execute(
        select(ExceptionRecord).where(
            ExceptionRecord.client_id == client_id,
            ExceptionRecord.year == year,
            ExceptionRecord.period == period,
        )
    )
    records = result.scalars().all()
    return [
        ExceptionPayload(
            employee_token=r.employee_token,
            run_id=f"{client_id}-{year}-{period}",
            annual_gross_salary=r.annual_gross_salary,
            expected_net_salary=r.expected_net_salary,
            actual_net_salary=r.actual_net_salary,
            variance_pct=r.variance_pct,
            flagged=r.flagged,
        )
        for r in records
    ]
