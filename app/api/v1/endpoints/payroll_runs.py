from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PayrollSummary
from app.db.session import get_db

router = APIRouter()


@router.get("/payroll-runs/years", response_model=list[int], tags=["payroll-runs"])
async def available_years(db: AsyncSession = Depends(get_db)) -> list[int]:
    result = await db.execute(
        select(PayrollSummary.year).distinct().order_by(PayrollSummary.year.desc())
    )
    return [row[0] for row in result.all()]
