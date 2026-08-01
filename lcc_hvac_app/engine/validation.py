from __future__ import annotations

from .models import Assumptions, Scenario


def validate_assumptions(assumptions: Assumptions) -> list[str]:
    warnings: list[str] = []
    if assumptions.airflow_m3_h_per_ahu <= 0:
        warnings.append("Airflow per AHU must be greater than 0.")
    if assumptions.number_of_ahu <= 0:
        warnings.append("Number of AHU must be greater than 0.")
    if assumptions.operating_hours_day < 0 or assumptions.operating_hours_day > 24:
        warnings.append("Operating hours/day must be between 0 and 24.")
    if assumptions.operating_days_year < 0 or assumptions.operating_days_year > 365:
        warnings.append("Operating days/year must be between 0 and 365.")
    if assumptions.fan_efficiency <= 0 or assumptions.fan_efficiency > 1:
        warnings.append("Fan efficiency must be greater than 0 and less than or equal to 1.")
    if assumptions.electricity_price_vnd_kwh < 0:
        warnings.append("Electricity price cannot be negative.")
    if assumptions.dust_concentration_mg_m3 < 0:
        warnings.append("Dust concentration cannot be negative.")
    if assumptions.environment_factor < 0:
        warnings.append("Environment factor cannot be negative.")
    if assumptions.labor_cost_vnd_filter_change < 0:
        warnings.append("Labor cost cannot be negative.")
    if assumptions.disposal_cost_vnd_filter_change < 0:
        warnings.append("Disposal cost cannot be negative.")
    if assumptions.downtime_cost_vnd_change < 0:
        warnings.append("Downtime cost cannot be negative.")
    if assumptions.co2_emission_factor_kg_kwh < 0:
        warnings.append("CO2 emission factor cannot be negative.")
    if assumptions.analysis_period_years <= 0:
        warnings.append("Analysis period must be greater than 0.")
    return warnings


def validate_scenario(scenario: Scenario) -> list[str]:
    warnings: list[str] = []
    if not scenario.stages:
        warnings.append(f"{scenario.name}: at least one filter stage is required.")
    for index, stage in enumerate(scenario.stages, start=1):
        label = f"{scenario.name} / row {index} / {stage.stage}"
        if not stage.stage:
            warnings.append(f"{label}: stage name is required.")
        if stage.qty_per_ahu <= 0:
            warnings.append(f"{label}: Qty/AHU must be greater than 0.")
        if stage.dhc_g <= 0:
            warnings.append(f"{label}: DHC must be greater than 0.")
        efficiency = stage.normalized_efficiency()
        if efficiency < 0 or efficiency > 1:
            warnings.append(f"{label}: Mass efficiency must be between 0 and 1, or 0 and 100%.")
        if stage.avg_dp_pa < 0:
            warnings.append(f"{label}: Avg DP cannot be negative.")
        if stage.price_vnd_filter < 0:
            warnings.append(f"{label}: Price/filter cannot be negative.")
    return warnings


def validate_project(assumptions: Assumptions, scenarios: list[Scenario]) -> list[str]:
    warnings = validate_assumptions(assumptions)
    names_seen: set[str] = set()
    for scenario in scenarios:
        normalized_name = scenario.name.strip().lower()
        if not normalized_name:
            warnings.append("Scenario name is required.")
        elif normalized_name in names_seen:
            warnings.append(f"{scenario.name}: scenario names must be unique.")
        names_seen.add(normalized_name)
        warnings.extend(validate_scenario(scenario))
    return warnings
