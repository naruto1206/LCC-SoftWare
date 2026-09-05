from __future__ import annotations

import pandas as pd
import streamlit as st


FORMULA_REFERENCE = [
    {
        "Result": "Dust entering",
        "Formula": "Airflow (m3/h) x Dust concentration (mg/m3) x Environment factor x Operating hours/day / 1000 / Qty per AHU",
        "Unit": "g/day/filter",
    },
    {
        "Result": "Dust captured",
        "Formula": "Dust entering x Mass efficiency",
        "Unit": "g/day/filter",
    },
    {
        "Result": "Dust to next stage",
        "Formula": "Dust entering - Dust captured",
        "Unit": "g/day/filter",
    },
    {
        "Result": "Filter life",
        "Formula": "Dust holding capacity / Dust captured",
        "Unit": "days",
    },
    {
        "Result": "Replacement/year",
        "Formula": "Operating days/year / Filter life",
        "Unit": "times/year",
    },
    {
        "Result": "Filter cost/year",
        "Formula": "Replacement/year x Price/filter x Qty per AHU x Number of AHU",
        "Unit": "currency/year",
    },
    {
        "Result": "Energy kWh/year",
        "Formula": "(Airflow / 3600) x Average pressure drop x Operating hours/year / (1000 x Fan efficiency) x Number of AHU",
        "Unit": "kWh/year",
    },
    {
        "Result": "Eurovent Avg DP",
        "Formula": "SUM(Dust increment dmi x Segment average DP) / Mx, where dmi = MIN(current dust fed, Mx) - MIN(previous dust fed, Mx)",
        "Unit": "Pa",
    },
    {
        "Result": "Energy cost/year",
        "Formula": "Energy kWh/year x Electricity price",
        "Unit": "currency/year",
    },
    {
        "Result": "Labor + disposal/year",
        "Formula": "Replacement/year x Qty per AHU x (Labor cost + Disposal cost) x Number of AHU + Replacement/year x Downtime cost x Number of AHU",
        "Unit": "currency/year",
    },
    {
        "Result": "CO2/year",
        "Formula": "Energy kWh/year x CO2 emission factor",
        "Unit": "kg/year",
    },
    {
        "Result": "TCO/year",
        "Formula": "Filter cost/year + Energy cost/year + Labor + disposal/year",
        "Unit": "currency/year",
    },
    {
        "Result": "Best option",
        "Formula": "Scenario with the lowest TCO/year",
        "Unit": "scenario",
    },
    {
        "Result": "Saving/year",
        "Formula": "Base TCO/year - Option TCO/year",
        "Unit": "currency/year",
    },
    {
        "Result": "Saving %",
        "Formula": "Saving/year / Base TCO/year x 100",
        "Unit": "%",
    },
]


FORMULA_BY_RESULT = {row["Result"]: row["Formula"] for row in FORMULA_REFERENCE}


def formula_text(result_name: str) -> str:
    return FORMULA_BY_RESULT[result_name]


def render_formula_note(result_name: str) -> None:
    st.markdown(
        f'<div class="formula-note"><strong>Formula:</strong> {formula_text(result_name)}</div>',
        unsafe_allow_html=True,
    )


def render_formula_reference(expanded: bool = False) -> None:
    with st.expander("Formula Reference", expanded=expanded):
        st.dataframe(
            pd.DataFrame(FORMULA_REFERENCE),
            width="stretch",
            hide_index=True,
        )
