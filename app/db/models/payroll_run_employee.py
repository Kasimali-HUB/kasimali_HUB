from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PayrollRunEmployee(Base):
    """
    One row per employee per imported payroll run. This is real data -
    employee_id and employee_name are PII. Nothing in app/legislation or
    app/exceptions ever imports this table directly; the only path from
    here to anything AI-assisted is through build_exception_queue(),
    which converts each row to a pseudonymized ExceptionPayload before
    anything downstream ever sees it.
    """

    __tablename__ = "payroll_run_employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    year: Mapped[int] = mapped_column(Integer)
    period: Mapped[str] = mapped_column(String(20))
    employee_id: Mapped[str] = mapped_column(String(64))  # business key from the import file
    employee_name: Mapped[str] = mapped_column(String(255))
    annual_gross_salary: Mapped[float] = mapped_column(Float)
    actual_net_salary: Mapped[float] = mapped_column(Float)
