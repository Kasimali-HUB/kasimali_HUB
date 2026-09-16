"""
Orchestrates a full Netherlands payslip calculation: gross salary in,
net pay and total employer cost out, with every intermediate figure
exposed for auditability and for the exception-triage layer.
"""

from dataclasses import dataclass, field

from app.countries.nl.employer_cost import employer_social_premiums
from app.countries.nl.income_tax import annual_wage_tax_withheld


@dataclass
class PayslipInput:
    annual_gross_salary: float
    permanent_contract: bool = True
    large_employer: bool = True
    whk_rate: float | None = None
    pension_employer_contribution: float = 0.0  # annual amount, if applicable


@dataclass
class PayslipResult:
    annual_gross_salary: float
    wage_tax: dict[str, float]
    employer_premiums: dict[str, float]
    annual_net_salary: float
    total_employer_cost: float
    breakdown: dict[str, float] = field(default_factory=dict)


def calculate_nl_payslip(payslip_input: PayslipInput) -> PayslipResult:
    wage_tax = annual_wage_tax_withheld(payslip_input.annual_gross_salary)
    employer_premiums = employer_social_premiums(
        payslip_input.annual_gross_salary,
        permanent_contract=payslip_input.permanent_contract,
        large_employer=payslip_input.large_employer,
        whk_rate=payslip_input.whk_rate,
    )

    annual_net_salary = round(
        payslip_input.annual_gross_salary - wage_tax["wage_tax_withheld"], 2
    )
    total_employer_cost = round(
        payslip_input.annual_gross_salary
        + employer_premiums["total_employer_premiums"]
        + payslip_input.pension_employer_contribution,
        2,
    )

    return PayslipResult(
        annual_gross_salary=payslip_input.annual_gross_salary,
        wage_tax=wage_tax,
        employer_premiums=employer_premiums,
        annual_net_salary=annual_net_salary,
        total_employer_cost=total_employer_cost,
        breakdown={
            "gross": payslip_input.annual_gross_salary,
            "wage_tax_withheld": wage_tax["wage_tax_withheld"],
            "net": annual_net_salary,
            "employer_premiums": employer_premiums["total_employer_premiums"],
            "pension_employer": payslip_input.pension_employer_contribution,
            "total_employer_cost": total_employer_cost,
        },
    )
