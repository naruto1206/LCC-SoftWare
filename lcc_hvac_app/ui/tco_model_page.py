from __future__ import annotations

import pandas as pd
import streamlit as st

from lcc_hvac_app.ui.formatting import money, number
from lcc_hvac_app.ui.formula_reference import render_formula_note, render_formula_reference


MODEL_COLUMNS = [
    "Scenario",
    "Filter Stage",
    "Qty/AHU",
    "Width (mm)",
    "Height (mm)",
    "Face Area (m2)",
    "Media Area (m2)",
    "Face Velocity (m/s)",
    "Media Velocity (m/s)",
    "DHC (g)",
    "Mass Efficiency",
    "Avg DP (Pa)",
    "Dust Entering (g/day/filter)",
    "Dust Captured (g/day/filter)",
    "Filter Life (days)",
    "Replacement/year",
    "Filter Cost/year",
    "Energy kWh/year",
    "Energy Cost/year",
    "Labor + Disposal/year",
    "CO2 kg/year",
    "TCO/year",
]


def _stage_model_rows(stages: list[dict[str, object]], currency: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in stages:
        rows.append(
            {
                "Scenario": str(row["scenario"]),
                "Filter Stage": str(row["stage"]),
                "Qty/AHU": number(float(row["qty_per_ahu"]), 0),
                "Width (mm)": number(float(row.get("width_mm", 0)), 0),
                "Height (mm)": number(float(row.get("height_mm", 0)), 0),
                "Face Area (m2)": number(float(row.get("face_area_m2", 0)), 4),
                "Media Area (m2)": number(float(row.get("media_area_m2", 0)), 4),
                "Face Velocity (m/s)": number(float(row.get("face_velocity_m_s", 0)), 2),
                "Media Velocity (m/s)": number(float(row.get("media_velocity_m_s", 0)), 2),
                "DHC (g)": number(float(row["dhc_g"]), 0),
                "Mass Efficiency": f"{float(row['mass_efficiency']) * 100:,.1f}%",
                "Avg DP (Pa)": number(float(row["avg_dp_pa"]), 0),
                "Dust Entering (g/day/filter)": number(
                    float(row["dust_entering_day_filter"]), 2
                ),
                "Dust Captured (g/day/filter)": number(
                    float(row["dust_captured_day_filter"]), 2
                ),
                "Filter Life (days)": number(float(row["life_days"]), 1),
                "Replacement/year": number(float(row["replacement_year"]), 2),
                "Filter Cost/year": money(float(row["filter_cost_year"]), currency),
                "Energy kWh/year": number(float(row["energy_kwh_year"]), 0),
                "Energy Cost/year": money(float(row["energy_cost_year"]), currency),
                "Labor + Disposal/year": money(
                    float(row["labor_disposal_cost_year"]), currency
                ),
                "CO2 kg/year": number(float(row["co2_kg_year"]), 0),
                "TCO/year": money(float(row["tco_year"]), currency),
            }
        )
    return rows


def _raw_stage_dataframe(stages: list[dict[str, object]]) -> pd.DataFrame:
    columns = [
        "scenario",
        "stage",
        "qty_per_ahu",
        "width_mm",
        "height_mm",
        "face_area_m2",
        "media_area_m2",
        "face_velocity_m_s",
        "media_velocity_m_s",
        "dhc_g",
        "mass_efficiency",
        "avg_dp_pa",
        "dust_entering_day_filter",
        "dust_captured_day_filter",
        "life_days",
        "replacement_year",
        "filter_cost_year",
        "energy_kwh_year",
        "energy_cost_year",
        "labor_disposal_cost_year",
        "co2_kg_year",
        "tco_year",
    ]
    return pd.DataFrame(stages, columns=columns)


def _render_summary_metrics(summary: dict[str, object], currency: str) -> None:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_formula_note("Filter cost/year")
        st.metric("Filter cost/year", money(float(summary["filter_cost_year"]), currency))
    with col2:
        render_formula_note("Energy cost/year")
        st.metric("Energy cost/year", money(float(summary["energy_cost_year"]), currency))
    with col3:
        render_formula_note("Labor + disposal/year")
        st.metric(
            "Labor + disposal/year",
            money(float(summary["labor_disposal_cost_year"]), currency),
        )
    with col4:
        render_formula_note("TCO/year")
        st.metric("TCO/year", money(float(summary["tco_year"]), currency))


def render_tco_model(comparison: dict[str, object], currency: str) -> None:
    st.caption(
        "Stage-by-stage model for filter cost, energy cost, labor + disposal cost, "
        "replacement frequency, CO2, and total cost of ownership."
    )

    summaries = list(comparison.get("summaries", []))
    stages = list(comparison.get("stages", []))
    if not summaries or not stages:
        st.info("No TCO model is available yet. Please check assumptions and scenario inputs.")
        return

    render_formula_reference()

    stage_rows = _stage_model_rows(stages, currency)
    model_df = pd.DataFrame(stage_rows, columns=MODEL_COLUMNS)
    raw_df = _raw_stage_dataframe(stages)

    scenario_names = [str(summary["scenario"]) for summary in summaries]
    selected_scenarios = st.multiselect(
        "Scenario",
        scenario_names,
        default=scenario_names,
        help="Select the scenario groups to show in the TCO model table.",
    )
    if not selected_scenarios:
        st.warning("Please select at least one scenario.")
        return

    filtered_df = model_df[model_df["Scenario"].isin(selected_scenarios)]
    st.dataframe(filtered_df, width="stretch", hide_index=True)

    st.download_button(
        "Download TCO model CSV",
        data=raw_df[raw_df["scenario"].isin(selected_scenarios)]
        .to_csv(index=False)
        .encode("utf-8-sig"),
        file_name="tco_model_stage_breakdown.csv",
        mime="text/csv",
        width="stretch",
    )

    st.markdown("**Scenario Cost Breakdown**")
    tabs = st.tabs(scenario_names)
    for tab, summary in zip(tabs, summaries, strict=False):
        with tab:
            _render_summary_metrics(summary, currency)
            scenario_stages = filtered_df[
                filtered_df["Scenario"] == str(summary["scenario"])
            ]
            st.dataframe(scenario_stages, width="stretch", hide_index=True)
