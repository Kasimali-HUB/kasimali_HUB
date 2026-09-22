from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PayrollSummary(Base):
    """
    One row per client per payroll period. Deliberately aggregate-only -
    the dashboard's three charts (headcount, total gross, employer cost)
    never need a per-employee breakdown, so this table never stores one.
    """

    __tablename__ = "payroll_summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    year: Mapped[int] = mapped_column(Integer)
    period: Mapped[str] = mapped_column(String(20))  # e.g. "2026-03"
    headcount: Mapped[int] = mapped_column(Integer)
    total_gross: Mapped[float] = mapped_column(Float)
    employer_cost: Mapped[float] = mapped_column(Float)

    client: Mapped["Client"] = relationship(back_populates="payroll_summaries")
