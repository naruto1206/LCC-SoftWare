from __future__ import annotations

import pandas as pd
import streamlit as st

from lcc_hvac_app.ui.formatting import money
from lcc_hvac_app.ui.formula_reference import render_formula_reference


SUMMARY_COLUMNS = [
    "scenario",
    "filter_cost_year",
    "energy_cost_year",
    "labor_disposal_cost_year",
    "tco_year",
    "saving_vs_base",
    "saving_percent",
    "energy_kwh_year",
    "co2_kg_year",
    "tco_3_years",
    "tco_5_years",
]


STAGE_COLUMNS = [
    "scenario",
    "stage",
    "qty_per_ahu",
    "rated_airflow_m3_h_filter",
    "airflow_per_filter_m3_h",
    "airflow_loading_percent",
    "target_filter_life_days",
    "filter_life_source",
    "width_mm",
    "height_mm",
    "face_area_m2",
    "media_area_m2",
    "face_velocity_m_s",
    "media_velocity_m_s",
    "dust_entering_day_filter",
    "dust_captured_day_filter",
    "life_days",
    "replacement_year",
    "filter_cost_year",
    "energy_cost_year",
    "labor_disposal_cost_year",
    "tco_year",
]


def render_results(comparison: dict[str, object], currency: str) -> None:
    summaries = pd.DataFrame(comparison["summaries"])
    stages = pd.DataFrame(comparison["stages"])
    if summaries.empty:
        st.info("No results yet.")
        return

    render_formula_reference()

    st.markdown("**Scenario Comparison**")
    st.dataframe(summaries[SUMMARY_COLUMNS], width="stretch", hide_index=True)

    best = comparison.get("best_option")
    best_row = summaries[summaries["scenario"] == best].iloc[0]
    st.success(
        f"Best option: {best} with TCO/year {money(float(best_row['tco_year']), currency)} "
        f"and saving {money(float(best_row['saving_vs_base']), currency)}."
    )

    st.markdown("**Stage-Level Calculation Detail**")
    st.dataframe(stages[STAGE_COLUMNS], width="stretch", hide_index=True)
