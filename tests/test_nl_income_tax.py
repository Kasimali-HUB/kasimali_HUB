from app.countries.nl.income_tax import (
    algemene_heffingskorting,
    arbeidskorting,
    box1_tax,
)
from app.countries.nl.rates import BOX1_BRACKETS


def test_box1_tax_zero_income():
    assert box1_tax(0) == 0.0


def test_box1_tax_within_first_bracket():
    income = 20_000
    expected = round(income * BOX1_BRACKETS[0].rate, 2)
    assert box1_tax(income) == expected


def test_box1_tax_bracket_boundary_is_additive():
    # Tax at the top of bracket 2 must equal bracket-1 tax plus bracket-2 tax
    # on the portion that falls in bracket 2 - catches off-by-one bracket bugs.
    b1, b2, _ = BOX1_BRACKETS
    tax_at_b1_top = box1_tax(b1.upper)
    tax_at_b2_top = box1_tax(b2.upper)
    expected_increment = round((b2.upper - b1.upper) * b2.rate, 2)
    assert round(tax_at_b2_top - tax_at_b1_top, 2) == expected_increment


def test_box1_tax_is_monotonic():
    incomes = [0, 10_000, 38_883, 60_000, 78_426, 150_000]
    taxes = [box1_tax(i) for i in incomes]
    assert taxes == sorted(taxes)


def test_algemene_heffingskorting_max_below_threshold():
    assert algemene_heffingskorting(20_000) == 3_115.0


def test_algemene_heffingskorting_zero_above_phaseout_end():
    assert algemene_heffingskorting(78_426) == 0.0
    assert algemene_heffingskorting(100_000) == 0.0


def test_algemene_heffingskorting_phases_out():
    low = algemene_heffingskorting(30_000)
    high = algemene_heffingskorting(70_000)
    assert 0 < high < low < 3_115.0


def test_arbeidskorting_zero_at_zero_income():
    assert arbeidskorting(0) == 0.0


def test_arbeidskorting_zero_above_cap():
    assert arbeidskorting(132_920) == 0.0
    assert arbeidskorting(200_000) == 0.0


def test_arbeidskorting_peaks_then_declines():
    at_peak = arbeidskorting(45_592)
    below_peak = arbeidskorting(25_845)
    above_peak = arbeidskorting(80_000)
    assert below_peak < at_peak
    assert above_peak < at_peak
