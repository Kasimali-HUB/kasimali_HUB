"""Employer-side social insurance premiums for Netherlands, tax year 2026."""

from app.countries.nl.rates import (
    AOF_HIGH,
    AOF_LOW,
    AWF_HIGH,
    AWF_LOW,
    MAX_PREMIELOON,
    WHK_SECTOR_AVERAGE,
    ZVW_EMPLOYER,
)


def employer_social_premiums(
    annual_gross_income: float,
    *,
    permanent_contract: bool = True,
    large_employer: bool = True,
    whk_rate: float | None = None,
) -> dict[str, float]:
    """
    Employer premiums are levied on gross income up to MAX_PREMIELOON only.

    whk_rate: pass the client's actual assessed Whk rate when known. Falls
    back to the published sector average, which is NOT accurate for a
    specific employer and must be replaced before this is used for a real
    client's payroll.
    """
    premie_grondslag = min(annual_gross_income, MAX_PREMIELOON)

    awf_rate = AWF_LOW if permanent_contract else AWF_HIGH
    aof_rate = AOF_HIGH if large_employer else AOF_LOW
    whk = whk_rate if whk_rate is not None else WHK_SECTOR_AVERAGE

    awf = round(premie_grondslag * awf_rate, 2)
    aof = round(premie_grondslag * aof_rate, 2)
    whk_amount = round(premie_grondslag * whk, 2)
    zvw = round(premie_grondslag * ZVW_EMPLOYER, 2)

    total = round(awf + aof + whk_amount + zvw, 2)

    return {
        "premie_grondslag": premie_grondslag,
        "awf": awf,
        "aof": aof,
        "whk": whk_amount,
        "zvw_employer": zvw,
        "total_employer_premiums": total,
    }
