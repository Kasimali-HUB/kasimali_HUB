"""
Raw payroll run record - lives entirely on the "your systems" side of the
privacy boundary. This is what a real payroll run produces per employee.

This will move to a proper SQLAlchemy model (app/db/models) once persistence
is wired up; kept as a plain dataclass for now so Phase 3 can be built and
tested independently of that.
"""

from dataclasses import dataclass


@dataclass
class PayrollRunRecord:
    employee_id: str  # internal DB identifier - never sent to the AI layer
    employee_name: str  # PII - never sent to the AI layer
    annual_gross_salary: float
    actual_net_salary: float  # what the payroll run actually produced
