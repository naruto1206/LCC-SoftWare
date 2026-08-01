from lcc_hvac_app.engine.models import Assumptions, FilterStage, Scenario
from lcc_hvac_app.engine.scenario import compare_scenarios
from lcc_hvac_app.engine.tco import calculate_scenario_tco


def test_scenario_tco_contains_stage_and_summary_results():
    assumptions = Assumptions(
        airflow_m3_h_per_ahu=10000,
        number_of_ahu=1,
        operating_hours_day=24,
        operating_days_year=365,
        fan_efficiency=0.6,
        electricity_price_vnd_kwh=2500,
        dust_concentration_mg_m3=0.3,
    )
    scenario = Scenario(
        "Base / Current",
        [FilterStage("Pre-filter", 4, 500, 0.5, 80, 100000)],
    )

    result = calculate_scenario_tco(scenario, assumptions)

    assert result["summary"]["tco_year"] > 0
    assert result["summary"]["energy_kwh_year"] > 0
    assert len(result["stages"]) == 1
    assert result["stages"][0]["replacement_year"] > 0


def test_compare_scenarios_calculates_saving_against_base():
    assumptions = Assumptions()
    base = Scenario("Base / Current", [FilterStage("Pre-filter", 8, 450, 0.55, 120, 110000)])
    option = Scenario("Option 1", [FilterStage("Pre-filter", 8, 900, 0.55, 60, 110000)])

    comparison = compare_scenarios([base, option], assumptions)
    option_summary = comparison["summaries"][1]

    assert comparison["best_option"] == "Option 1"
    assert option_summary["saving_vs_base"] > 0
    assert option_summary["saving_percent"] > 0
