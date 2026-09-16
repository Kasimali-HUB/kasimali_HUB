"""
Box 1 wage tax (loonheffing) calculation for Netherlands, tax year 2026.

Note: the combined wage-tax-plus-national-insurance rate is already folded
into the Box 1 bracket percentages (for both AOW and non-AOW employees), so
there is no separate AOW/ANW/Wlz deduction line to compute here.
"""

from app.countries.nl.rates import (
    ALGEMENE_HEFFINGSKORTING_AOW_MAX,
    ALGEMENE_HEFFINGSKORTING_AOW_PHASEOUT_RATE,
    ALGEMENE_HEFFINGSKORTING_MAX,
    ALGEMENE_HEFFINGSKORTING_PHASEOUT_END,
    ALGEMENE_HEFFINGSKORTING_PHASEOUT_RATE,
    ALGEMENE_HEFFINGSKORTING_PHASEOUT_START,
    ARBEIDSKORTING_SEGMENTS,
    BOX1_BRACKETS,
    BOX1_BRACKETS_AOW_BORN_BEFORE_1946,
    BOX1_BRACKETS_AOW_BORN_ON_OR_AFTER_1946,
)


def _brackets_for(is_aow_age: bool, born_before_1946: bool):
    if not is_aow_age:
        return BOX1_BRACKETS
    return (
        BOX1_BRACKETS_AOW_BORN_BEFORE_1946
        if born_before_1946
        else BOX1_BRACKETS_AOW_BORN_ON_OR_AFTER_1946
    )


def box1_tax(
    annual_taxable_income: float,
    *,
    is_aow_age: bool = False,
    born_before_1946: bool = False,
) -> float:
    """Gross Box 1 tax before any credits, using the 2026 progressive brackets."""
    if annual_taxable_income <= 0:
        return 0.0

    brackets = _brackets_for(is_aow_age, born_before_1946)
    tax = 0.0
    for bracket in brackets:
        upper = bracket.upper if bracket.upper is not None else annual_taxable_income
        if annual_taxable_income <= bracket.lower:
            break
        taxable_in_bracket = min(annual_taxable_income, upper) - bracket.lower
        tax += taxable_in_bracket * bracket.rate
    return round(tax, 2)


def algemene_heffingskorting(annual_income: float, *, is_aow_age: bool = False) -> float:
    """General tax credit, phased out between the 2026 thresholds."""
    max_credit = ALGEMENE_HEFFINGSKORTING_AOW_MAX if is_aow_age else ALGEMENE_HEFFINGSKORTING_MAX
    phaseout_rate = (
        ALGEMENE_HEFFINGSKORTING_AOW_PHASEOUT_RATE
        if is_aow_age
        else ALGEMENE_HEFFINGSKORTING_PHASEOUT_RATE
    )

    if annual_income <= ALGEMENE_HEFFINGSKORTING_PHASEOUT_START:
        return max_credit
    if annual_income >= ALGEMENE_HEFFINGSKORTING_PHASEOUT_END:
        return 0.0
    reduction = (annual_income - ALGEMENE_HEFFINGSKORTING_PHASEOUT_START) * phaseout_rate
    return round(max(0.0, max_credit - reduction), 2)


def arbeidskorting(annual_labor_income: float) -> float:
    """
    Labor tax credit, 2026 piecewise schedule.

    Applied the same way regardless of AOW status - no AOW-specific
    arbeidskorting table was found during research; see rates.py docstring.
    """
    if annual_labor_income <= 0:
        return 0.0

    for segment in ARBEIDSKORTING_SEGMENTS:
        upper = segment.upper if segment.upper is not None else float("inf")
        if segment.lower <= annual_labor_income < upper or (
            segment.upper is None and annual_labor_income >= segment.lower
        ):
            value = segment.base + segment.rate * (annual_labor_income - segment.lower)
            return round(max(0.0, value), 2)
    return 0.0


def annual_wage_tax_withheld(
    annual_gross_income: float,
    *,
    is_aow_age: bool = False,
    born_before_1946: bool = False,
) -> dict[str, float]:
    """
    Full loonheffing calculation: gross Box 1 tax minus applicable credits.
    Returns a breakdown so the calling code (and any exception-triage layer)
    can see each component, not just the final number.
    """
    gross_tax = box1_tax(
        annual_gross_income, is_aow_age=is_aow_age, born_before_1946=born_before_1946
    )
    ahk = algemene_heffingskorting(annual_gross_income, is_aow_age=is_aow_age)
    ak = arbeidskorting(annual_gross_income)
    withheld = max(0.0, round(gross_tax - ahk - ak, 2))

    return {
        "gross_box1_tax": gross_tax,
        "algemene_heffingskorting": ahk,
        "arbeidskorting": ak,
        "wage_tax_withheld": withheld,
    }
