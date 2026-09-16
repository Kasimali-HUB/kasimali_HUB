from app.countries.nl.employer_cost import employer_social_premiums
from app.countries.nl.rates import MAX_PREMIELOON


def test_premiums_are_capped_at_max_premieloon():
    below_cap = employer_social_premiums(50_000)
    at_cap = employer_social_premiums(MAX_PREMIELOON)
    above_cap = employer_social_premiums(200_000)

    assert at_cap["total_employer_premiums"] == above_cap["total_employer_premiums"]
    assert below_cap["total_employer_premiums"] < at_cap["total_employer_premiums"]


def test_flexible_contract_costs_more_than_permanent():
    permanent = employer_social_premiums(50_000, permanent_contract=True)
    flexible = employer_social_premiums(50_000, permanent_contract=False)
    assert flexible["awf"] > permanent["awf"]


def test_custom_whk_rate_overrides_sector_average():
    default_rate = employer_social_premiums(50_000)
    custom_rate = employer_social_premiums(50_000, whk_rate=0.03)
    assert custom_rate["whk"] > default_rate["whk"]


def test_total_equals_sum_of_components():
    result = employer_social_premiums(50_000)
    component_sum = round(
        result["awf"] + result["aof"] + result["whk"] + result["zvw_employer"], 2
    )
    assert result["total_employer_premiums"] == component_sum
