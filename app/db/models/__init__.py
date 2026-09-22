"""Import every model here so relationship() string references resolve
and Base.metadata.create_all() picks up all tables."""

from app.db.models.client import Client
from app.db.models.payroll_summary import PayrollSummary

__all__ = ["Client", "PayrollSummary"]
