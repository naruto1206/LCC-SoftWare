from __future__ import annotations

from .co2 import calculate_co2_year
from .cost import calculate_filter_cost_year, calculate_labor_disposal_cost_year
from .dust import calculate_dust_captured, calculate_dust_entering, calculate_dust_to_next_stage
from .energy import calculate_energy_cost_year, calculate_energy_kwh_year
from .filter_life import calculate_filter_life_days, calculate_replacement_per_year
from .models import Assumptions, FilterStage, Scenario


def calculate_stage_tco(
    stage: FilterStage,
    assumptions: Assumptions,
    dust_entering_day_filter: float,
) -> dict[str, float | str]:
    dust_captured = calculate_dust_captured(dust_entering_day_filter, stage.normalized_efficiency())
    dust_to_next = calculate_dust_to_next_stage(dust_entering_day_filter, dust_captured)
    life_days = calculate_filter_life_days(stage.dhc_g, dust_captured)
    replacement_year = calculate_replacement_per_year(
        assumptions.operating_days_year, life_days
    )
    filter_cost = calculate_filter_cost_year(
        replacement_year,
        stage.price_vnd_filter,
        stage.qty_per_ahu,
        assumptions.number_of_ahu,
    )
    labor_disposal_cost = calculate_labor_disposal_cost_year(
        replacement_year,
        stage.qty_per_ahu,
        assumptions.labor_cost_vnd_filter_change,
        assumptions.disposal_cost_vnd_filter_change,
        assumptions.downtime_cost_vnd_change,
        assumptions.number_of_ahu,
    )
    energy_kwh = calculate_energy_kwh_year(
        assumptions.airflow_m3_h_per_ahu,
        stage.avg_dp_pa,
        assumptions.operating_hours_day,
        assumptions.operating_days_year,
        assumptions.fan_efficiency,
        assumptions.number_of_ahu,
    )
    energy_cost = calculate_energy_cost_year(
        energy_kwh, assumptions.electricity_price_vnd_kwh
    )
    co2 = calculate_co2_year(energy_kwh, assumptions.co2_emission_factor_kg_kwh)
    tco_year = filter_cost + energy_cost + labor_disposal_cost
    return {
        "stage": stage.stage,
        "qty_per_ahu": stage.qty_per_ahu,
        "dhc_g": stage.dhc_g,
        "mass_efficiency": stage.normalized_efficiency(),
        "avg_dp_pa": stage.avg_dp_pa,
        "price_vnd_filter": stage.price_vnd_filter,
        "dust_entering_day_filter": dust_entering_day_filter,
        "dust_captured_day_filter": dust_captured,
        "dust_to_next_stage_day_filter": dust_to_next,
        "life_days": life_days,
        "replacement_year": replacement_year,
        "filter_cost_year": filter_cost,
        "energy_kwh_year": energy_kwh,
        "energy_cost_year": energy_cost,
        "labor_disposal_cost_year": labor_disposal_cost,
        "co2_kg_year": co2,
        "tco_year": tco_year,
    }


def calculate_scenario_tco(
    scenario: Scenario, assumptions: Assumptions
) -> dict[str, object]:
    stage_results = []
    incoming_total_per_ahu = None
    for index, stage in enumerate(scenario.stages):
        if index == 0:
            dust_entering = calculate_dust_entering(
                assumptions.airflow_m3_h_per_ahu,
                assumptions.dust_concentration_mg_m3,
                assumptions.environment_factor,
                assumptions.operating_hours_day,
                stage.qty_per_ahu,
            )
        else:
            dust_entering = (incoming_total_per_ahu or 0.0) / stage.qty_per_ahu

        result = calculate_stage_tco(stage, assumptions, dust_entering)
        incoming_total_per_ahu = (
            float(result["dust_to_next_stage_day_filter"]) * stage.qty_per_ahu
        )
        stage_results.append(result)

    summary = {
        "scenario": scenario.name,
        "filter_cost_year": sum(float(row["filter_cost_year"]) for row in stage_results),
        "energy_kwh_year": sum(float(row["energy_kwh_year"]) for row in stage_results),
        "energy_cost_year": sum(float(row["energy_cost_year"]) for row in stage_results),
        "labor_disposal_cost_year": sum(
            float(row["labor_disposal_cost_year"]) for row in stage_results
        ),
        "co2_kg_year": sum(float(row["co2_kg_year"]) for row in stage_results),
        "tco_year": sum(float(row["tco_year"]) for row in stage_results),
    }
    summary["tco_3_years"] = summary["tco_year"] * 3
    summary["tco_5_years"] = summary["tco_year"] * 5
    summary["analysis_period_tco"] = summary["tco_year"] * assumptions.analysis_period_years
    return {"summary": summary, "stages": stage_results}
