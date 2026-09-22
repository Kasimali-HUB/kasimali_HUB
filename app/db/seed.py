"""
Seeds a small, obviously-fake demo dataset: a couple of clients and a
handful of aggregate payroll summaries across two years, so the dashboard
has something real to render against in dev and in tests.

Nothing here is a real client. Replace entirely once real client
onboarding exists.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Client, PayrollSummary

DEMO_CLIENTS = ["Noorderlicht B.V.", "Delta Logistics NL"]

DEMO_SUMMARIES = [
    # (client_index, year, period, headcount, total_gross, employer_cost)
    (0, 2025, "2025-01", 42, 168_000, 200_000),
    (0, 2025, "2025-06", 45, 182_000, 216_000),
    (0, 2026, "2026-01", 48, 196_000, 233_000),
    (0, 2026, "2026-03", 50, 205_000, 244_000),
    (1, 2025, "2025-01", 18, 81_000, 96_000),
    (1, 2025, "2025-06", 20, 92_000, 109_000),
    (1, 2026, "2026-01", 22, 101_000, 120_000),
    (1, 2026, "2026-03", 23, 106_000, 126_000),
]


async def seed_demo_data(session: AsyncSession) -> None:
    clients = [Client(name=name) for name in DEMO_CLIENTS]
    session.add_all(clients)
    await session.flush()  # assigns IDs without committing yet

    summaries = [
        PayrollSummary(
            client_id=clients[client_index].id,
            year=year,
            period=period,
            headcount=headcount,
            total_gross=total_gross,
            employer_cost=employer_cost,
        )
        for client_index, year, period, headcount, total_gross, employer_cost in DEMO_SUMMARIES
    ]
    session.add_all(summaries)
    await session.commit()
