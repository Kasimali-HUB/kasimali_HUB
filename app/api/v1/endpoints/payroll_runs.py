from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import Client, PayrollSummary
from app.db.session import get_db
from app.payroll.csv_import import CsvValidationError, parse_payroll_csv
from app.payroll.import_service import import_payroll_run
from app.schemas.payroll_runs import ImportResultOut, PayrollRunOut

router = APIRouter()
settings = get_settings()


@router.get("/payroll-runs/years", response_model=list[int], tags=["payroll-runs"])
async def available_years(db: AsyncSession = Depends(get_db)) -> list[int]:
    result = await db.execute(
        select(PayrollSummary.year).distinct().order_by(PayrollSummary.year.desc())
    )
    return [row[0] for row in result.all()]


@router.get("/payroll-runs", response_model=list[PayrollRunOut], tags=["payroll-runs"])
async def list_payroll_runs(db: AsyncSession = Depends(get_db)) -> list[PayrollRunOut]:
    """Every imported run, newest first - powers the run picker on Exception Review."""
    result = await db.execute(
        select(PayrollSummary, Client.name)
        .join(Client, Client.id == PayrollSummary.client_id)
        .order_by(PayrollSummary.year.desc(), PayrollSummary.period.desc())
    )
    return [
        PayrollRunOut(client_id=summary.client_id, client_name=name, year=summary.year, period=summary.period)
        for summary, name in result.all()
    ]


@router.post("/payroll-runs/import", response_model=ImportResultOut, tags=["payroll-runs"])
async def import_payroll(
    client_id: int,
    year: int,
    period: str,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
) -> ImportResultOut:
    client = await db.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail=f"No client with id {client_id}")

    file_bytes = await file.read()
    try:
        rows = parse_payroll_csv(file_bytes)
    except CsvValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result = await import_payroll_run(
        db,
        client_id=client_id,
        year=year,
        period=period,
        rows=rows,
        pseudonymization_secret=settings.pseudonymization_secret,
    )
    return ImportResultOut(
        headcount=result.headcount,
        total_gross=result.total_gross,
        employer_cost=result.employer_cost,
        flagged_count=result.flagged_count,
    )
