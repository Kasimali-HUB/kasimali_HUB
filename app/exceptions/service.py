"""
Builds the exception queue from real payroll run records.

This is the piece that turns the "your systems / AI layer" diagram into
actual code: it's the only function that is allowed to see both the real
records (with names) and produce something safe to hand to an AI-assisted
component. Everything on the other side of this function only ever sees
ExceptionPayload objects.
"""

from app.countries.nl.payroll import PayslipInput, calculate_nl_payslip
from app.exceptions.records import PayrollRunRecord
from app.exceptions.schemas import ExceptionPayload
from app.privacy.pseudonymize import pseudonymize

DEFAULT_VARIANCE_TOLERANCE = 0.02  # 2% - tune per client/country as needed


def build_exception_queue(
    records: list[PayrollRunRecord],
    *,
    run_id: str,
    pseudonymization_secret: str,
    tolerance: float = DEFAULT_VARIANCE_TOLERANCE,
) -> tuple[list[ExceptionPayload], dict[str, str]]:
    """
    Returns:
      - payloads: safe to pass anywhere, including an AI-assisted layer.
      - token_map: {employee_token: employee_id}, kept LOCAL ONLY. This is
        how an associate resolves "EMP-a1b2c3" back to a real person -
        never pass this dict to anything outside your own systems.
    """
    payloads: list[ExceptionPayload] = []
    token_map: dict[str, str] = {}

    for record in records:
        expected = calculate_nl_payslip(
            PayslipInput(annual_gross_salary=record.annual_gross_salary)
        )
        expected_net = expected.annual_net_salary
        variance_pct = (
            round((record.actual_net_salary - expected_net) / expected_net, 4)
            if expected_net
            else 0.0
        )
        token = pseudonymize(record.employee_id, pseudonymization_secret)
        token_map[token] = record.employee_id

        payloads.append(
            ExceptionPayload(
                employee_token=token,
                run_id=run_id,
                annual_gross_salary=record.annual_gross_salary,
                expected_net_salary=expected_net,
                actual_net_salary=record.actual_net_salary,
                variance_pct=variance_pct,
                flagged=abs(variance_pct) > tolerance,
            )
        )

    return payloads, token_map


def flagged_only(payloads: list[ExceptionPayload]) -> list[ExceptionPayload]:
    return [p for p in payloads if p.flagged]
