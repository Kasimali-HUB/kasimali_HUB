"""
ExceptionPayload is the *only* shape of data allowed to reach the AI-assisted
triage layer. It has no name, no employee_id, no client identifier - just a
pseudonymized token and numbers. This is enforced by construction: nothing
downstream can leak PII through this type, because the type has nowhere to
put it.
"""

from pydantic import BaseModel


class ExceptionPayload(BaseModel):
    employee_token: str  # pseudonymized, see app/privacy/pseudonymize.py
    run_id: str
    annual_gross_salary: float
    expected_net_salary: float
    actual_net_salary: float
    variance_pct: float
    flagged: bool
