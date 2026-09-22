from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Client, PayrollSummary
from app.db.session import get_db
from app.schemas.dashboard import ChartPoint, DashboardSummary

router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardSummary, tags=["dashboard"])
async def dashboard_summary(
    client_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    total_client_count = (
        await db.execute(select(func.count()).select_from(Client))
    ).scalar_one()

    query = select(PayrollSummary).order_by(PayrollSummary.period)
    if client_id is not None:
        query = query.where(PayrollSummary.client_id == client_id)

    rows = (await db.execute(query)).scalars().all()

    if client_id is not None:
        # Single client selected: one point per period, no aggregation needed.
        headcount = [ChartPoint(period=r.period, year=r.year, value=r.headcount) for r in rows]
        gross = [ChartPoint(period=r.period, year=r.year, value=r.total_gross) for r in rows]
        cost = [ChartPoint(period=r.period, year=r.year, value=r.employer_cost) for r in rows]
    else:
        # "All clients": sum each metric per period across every client.
        by_period: dict[str, dict[str, float]] = defaultdict(
            lambda: {"year": 0, "headcount": 0, "total_gross": 0, "employer_cost": 0}
        )
        for r in rows:
            bucket = by_period[r.period]
            bucket["year"] = r.year
            bucket["headcount"] += r.headcount
            bucket["total_gross"] += r.total_gross
            bucket["employer_cost"] += r.employer_cost

        periods = sorted(by_period.keys())
        headcount = [ChartPoint(period=p, year=by_period[p]["year"], value=by_period[p]["headcount"]) for p in periods]
        gross = [ChartPoint(period=p, year=by_period[p]["year"], value=by_period[p]["total_gross"]) for p in periods]
        cost = [ChartPoint(period=p, year=by_period[p]["year"], value=by_period[p]["employer_cost"]) for p in periods]

    return DashboardSummary(
        total_client_count=total_client_count,
        selected_client_id=client_id,
        headcount_series=headcount,
        total_gross_series=gross,
        employer_cost_series=cost,
    )
