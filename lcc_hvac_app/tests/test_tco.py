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


def test_tco_engine_matches_excel_tco_model_option_1_sample():
    assumptions = Assumptions(
        airflow_m3_h_per_ahu=20000,
        number_of_ahu=1,
        operating_hours_day=24,
        operating_days_year=365,
        fan_efficiency=0.65,
        electricity_price_vnd_kwh=3000,
        dust_concentration_mg_m3=0.15,
        environment_factor=1,
        labor_cost_vnd_filter_change=100000,
        disposal_cost_vnd_filter_change=20000,
        downtime_cost_vnd_change=0,
        co2_emission_factor_kg_kwh=0.6766,
        analysis_period_years=5,
    )
    scenario = Scenario(
        "Excel Option 1",
        [
            FilterStage("Pre-filter", 20, 600, 0.7, 85, 250000),
            FilterStage("Fine-filter", 20, 350, 0.75, 110, 1500000),
            FilterStage("HEPA", 20, 500, 0.95, 350, 3800000),
        ],
    )

    result = calculate_scenario_tco(scenario, assumptions)

    assert result["summary"]["filter_cost_year"] == 47_237_048.571428575
    assert result["summary"]["energy_cost_year"] == 122_415_384.61538461
    assert result["summary"]["labor_disposal_cost_year"] == 6_155_902.285714285
    assert result["summary"]["tco_year"] == 175_808_335.47252747


def test_stage_tco_includes_geometry_checks():
    assumptions = Assumptions(
        airflow_m3_h_per_ahu=20000,
        number_of_ahu=1,
        operating_hours_day=24,
        operating_days_year=365,
        fan_efficiency=0.6,
        electricity_price_vnd_kwh=2500,
        dust_concentration_mg_m3=0.3,
    )
    scenario = Scenario(
        "Geometry check",
        [
            FilterStage(
                "Pre-filter",
                qty_per_ahu=20,
                dhc_g=600,
                mass_efficiency=0.7,
                avg_dp_pa=85,
                price_vnd_filter=250000,
                width_mm=592,
                height_mm=592,
                media_area_m2=0.3505,
                rated_airflow_m3_h_filter=1000,
            )
        ],
    )

    stage = calculate_scenario_tco(scenario, assumptions)["stages"][0]

    assert round(stage["face_area_m2"], 4) == 0.3505
    assert round(stage["total_face_area_m2"], 3) == 7.009
    assert stage["airflow_per_filter_m3_h"] == 1000
    assert stage["rated_airflow_m3_h_filter"] == 1000
    assert stage["airflow_loading_percent"] == 100
    assert round(stage["face_velocity_m_s"], 2) == 0.79
    assert round(stage["media_velocity_m_s"], 2) == 0.79
