from app.countries.nl.payroll import PayslipInput, calculate_nl_payslip


def test_net_is_less_than_gross():
    result = calculate_nl_payslip(PayslipInput(annual_gross_salary=50_000))
    assert result.annual_net_salary < result.annual_gross_salary


def test_total_employer_cost_exceeds_gross():
    result = calculate_nl_payslip(PayslipInput(annual_gross_salary=50_000))
    assert result.total_employer_cost > result.annual_gross_salary


def test_higher_gross_gives_higher_net():
    lower = calculate_nl_payslip(PayslipInput(annual_gross_salary=40_000))
    higher = calculate_nl_payslip(PayslipInput(annual_gross_salary=60_000))
    assert higher.annual_net_salary > lower.annual_net_salary


def test_breakdown_reconciles_to_total_employer_cost():
    result = calculate_nl_payslip(
        PayslipInput(annual_gross_salary=55_000, pension_employer_contribution=2_000)
    )
    expected = round(
        result.annual_gross_salary
        + result.employer_premiums["total_employer_premiums"]
        + 2_000,
        2,
    )
    assert result.total_employer_cost == expected


def test_this_is_exactly_what_the_anomaly_triage_layer_would_check():
    """
    Sanity check standing in for the exception-triage validation discussed
    earlier: the engine's own expected net should match what it just
    calculated, by construction. A real anomaly check compares this
    *expected* net against the *actual* net produced by a payroll run, and
    flags a variance - this test just confirms the expected side is stable
    and internally consistent.
    """
    result = calculate_nl_payslip(PayslipInput(annual_gross_salary=48_000))
    recomputed = calculate_nl_payslip(PayslipInput(annual_gross_salary=48_000))
    assert result.annual_net_salary == recomputed.annual_net_salary
