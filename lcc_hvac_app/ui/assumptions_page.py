from __future__ import annotations

import streamlit as st

from lcc_hvac_app.engine.efficiency import (
    OUTDOOR_ENVIRONMENT_PROFILES,
    environment_profile,
)
from lcc_hvac_app.engine.models import Assumptions


def render_assumptions(assumptions: Assumptions) -> Assumptions:
    current_environment = getattr(assumptions, "outdoor_environment", "Country town")
    environment_options = list(OUTDOOR_ENVIRONMENT_PROFILES.keys())
    environment_index = (
        environment_options.index(current_environment)
        if current_environment in environment_options
        else environment_options.index("Country town")
    )
    system_col, cost_col, service_col = st.columns(3)
    with system_col:
        st.markdown("**System Operation**")
        airflow = st.number_input("Airflow per AHU (m3/h)", min_value=0.0, value=float(assumptions.airflow_m3_h_per_ahu), step=1000.0)
        ahu = st.number_input("Number of AHU", min_value=1, value=int(assumptions.number_of_ahu), step=1)
        hours = st.number_input("Operating hours/day", min_value=0.0, max_value=24.0, value=float(assumptions.operating_hours_day), step=1.0)
        days = st.number_input("Operating days/year", min_value=0.0, max_value=365.0, value=float(assumptions.operating_days_year), step=1.0)
    with cost_col:
        st.markdown("**Energy and Air Quality**")
        fan_eff = st.number_input("Fan total efficiency", min_value=0.01, max_value=1.0, value=float(assumptions.fan_efficiency), step=0.01)
        electricity = st.number_input("Electricity price (VND/kWh)", min_value=0.0, value=float(assumptions.electricity_price_vnd_kwh), step=100.0)
        outdoor_environment = st.selectbox(
            "Outdoor Environment",
            environment_options,
            index=environment_index,
            help="This selection auto-fills dust concentration, environment factor, and the mass-efficiency estimation profile.",
        )
        profile = environment_profile(outdoor_environment)
        advanced_override = st.checkbox(
            "Advanced dust override",
            value=bool(getattr(assumptions, "advanced_dust_override", False)),
            help="Enable only when you have measured site dust data or a project-specific correction factor.",
        )
        if advanced_override:
            dust = st.number_input(
                "Dust concentration (mg/m3)",
                min_value=0.0,
                value=float(assumptions.dust_concentration_mg_m3),
                step=0.1,
            )
            env = st.number_input(
                "Environment factor",
                min_value=0.0,
                value=float(assumptions.environment_factor),
                step=0.1,
            )
        else:
            dust = profile.dust_concentration_mg_m3
            env = profile.environment_factor
            st.metric("Dust concentration", f"{dust:,.2f} mg/m3")
            st.metric("Environment factor", f"{env:,.2f}")
    with service_col:
        st.markdown("**Service Costs**")
        labor = st.number_input("Labor cost/filter/change", min_value=0.0, value=float(assumptions.labor_cost_vnd_filter_change), step=10000.0)
        disposal = st.number_input("Disposal cost/filter/change", min_value=0.0, value=float(assumptions.disposal_cost_vnd_filter_change), step=10000.0)
        downtime = st.number_input("Downtime cost/change", min_value=0.0, value=float(assumptions.downtime_cost_vnd_change), step=10000.0)
        co2 = st.number_input("CO2 emission factor (kg/kWh)", min_value=0.0, value=float(assumptions.co2_emission_factor_kg_kwh), step=0.01)
        period = st.number_input("Analysis period (years)", min_value=1, value=int(assumptions.analysis_period_years), step=1)

    return Assumptions(
        airflow_m3_h_per_ahu=airflow,
        number_of_ahu=ahu,
        operating_hours_day=hours,
        operating_days_year=days,
        fan_efficiency=fan_eff,
        electricity_price_vnd_kwh=electricity,
        outdoor_environment=outdoor_environment,
        advanced_dust_override=advanced_override,
        dust_concentration_mg_m3=dust,
        environment_factor=env,
        labor_cost_vnd_filter_change=labor,
        disposal_cost_vnd_filter_change=disposal,
        downtime_cost_vnd_change=downtime,
        co2_emission_factor_kg_kwh=co2,
        analysis_period_years=period,
    )
