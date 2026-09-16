from app.countries.nl.employer_cost import employer_social_premiums
from app.countries.nl.income_tax import algemene_heffingskorting, box1_tax
from app.countries.nl.payroll import PayslipInput, calculate_nl_payslip


def test_aow_first_bracket_matches_published_reference():
    # Published reference: 38,883 taxed at the AOW first-bracket rate
    # (born on/after 1946) gives exactly 6,940.62.
    assert box1_tax(38_883, is_aow_age=True) == 6_940.62


def test_non_aow_first_bracket_matches_published_reference():
    assert box1_tax(38_883) == 13_900.67


def test_aow_employee_pays_less_tax_than_non_aow_at_same_income():
    income = 50_000
    non_aow_tax = box1_tax(income)
    aow_tax = box1_tax(income, is_aow_age=True)
    assert aow_tax < non_aow_tax


def test_aow_born_before_1946_gets_wider_first_bracket():
    # At 40,000 income, "born before 1946" is still in the lower-rate
    # bracket (threshold 41,123) while "born on/after 1946" has crossed
    # into the second bracket (threshold 38,883) - so born-before-1946
    # owes less tax at this specific income.
    income = 40_000
    born_after = box1_tax(income, is_aow_age=True, born_before_1946=False)
    born_before = box1_tax(income, is_aow_age=True, born_before_1946=True)
    assert born_before < born_after


def test_aow_algemene_heffingskorting_max_is_lower():
    assert algemene_heffingskorting(20_000, is_aow_age=True) == 1_556.0
    assert algemene_heffingskorting(20_000, is_aow_age=False) == 3_115.0


def test_full_payslip_respects_aow_flag():
    non_aow = calculate_nl_payslip(PayslipInput(annual_gross_salary=50_000))
    aow = calculate_nl_payslip(
        PayslipInput(annual_gross_salary=50_000, is_aow_age=True)
    )
    # Less tax withheld for the AOW employee at the same gross salary.
    assert aow.wage_tax["wage_tax_withheld"] < non_aow.wage_tax["wage_tax_withheld"]
    assert aow.annual_net_salary > non_aow.annual_net_salary


def test_whk_flag_true_when_sector_average_used():
    result = employer_social_premiums(50_000)
    assert result["whk_is_sector_average"] is True


def test_whk_flag_false_when_client_rate_provided():
    result = employer_social_premiums(50_000, whk_rate=0.021)
    assert result["whk_is_sector_average"] is False
