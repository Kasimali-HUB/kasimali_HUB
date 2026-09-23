from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExceptionRecord(Base):
    """
    Persisted output of build_exception_queue() for one imported run.
    Deliberately the same shape as ExceptionPayload (app/exceptions/schemas)
    - a token and numbers, never a name or employee_id.
    """

    __tablename__ = "exception_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    year: Mapped[int] = mapped_column(Integer)
    period: Mapped[str] = mapped_column(String(20))
    employee_token: Mapped[str] = mapped_column(String(32))
    annual_gross_salary: Mapped[float] = mapped_column(Float)
    expected_net_salary: Mapped[float] = mapped_column(Float)
    actual_net_salary: Mapped[float] = mapped_column(Float)
    variance_pct: Mapped[float] = mapped_column(Float)
    flagged: Mapped[bool] = mapped_column(Boolean)
