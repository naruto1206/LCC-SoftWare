from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from lcc_hvac_app.ui.formatting import money, number
from lcc_hvac_app.ui.formula_reference import render_formula_note, render_formula_reference

CHART_COLORS = ["#0f9f8f", "#d99a2b", "#2f6f55", "#b45309", "#6d5f35", "#3f7f78"]


def compact_value(value: float, suffix: str = "") -> str:
    abs_value = abs(float(value))
    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B{suffix}"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M{suffix}"
    if abs_value >= 1_000:
        return f"{value / 1_000:.1f}K{suffix}"
    return f"{value:,.0f}{suffix}"


def apply_bar_value_style(fig: object) -> None:
    fig.update_traces(
        textposition="auto",
        textfont_size=11,
        cliponaxis=False,
    )
    fig.update_layout(uniformtext_minsize=9, uniformtext_mode="hide")
    fig.update_layout(
        paper_bgcolor="#fffaf0",
        plot_bgcolor="#fffaf0",
        font={"color": "#172033", "size": 12},
        title_font={"size": 16, "color": "#172033"},
        margin={"l": 24, "r": 24, "t": 56, "b": 48},
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=False, linecolor="#e1d8c6")
    fig.update_yaxes(gridcolor="#efe4ce", linecolor="#e1d8c6")


def render_dashboard(
    comparison: dict[str, object], currency: str, logo_path: Path | None = None
) -> None:
    summaries = pd.DataFrame(comparison["summaries"])
    stages = pd.DataFrame(comparison["stages"])
    if summaries.empty:
        st.info("No dashboard data yet.")
        return

    best_name = comparison.get("best_option")
    base = summaries.iloc[0]
    best = summaries[summaries["scenario"] == best_name].iloc[0]

    render_formula_reference()

    st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        render_formula_note("TCO/year")
        st.metric("Base TCO/year", money(float(base["tco_year"]), currency))
    with kpi2:
        render_formula_note("Best option")
        st.metric("Best option", str(best_name))
    with kpi3:
        render_formula_note("Saving/year")
        st.metric(
            "Saving/year",
            money(float(best["saving_vs_base"]), currency),
            f"{float(best['saving_percent']):.1f}%",
        )
    with kpi4:
        render_formula_note("CO2/year")
        st.metric("CO2/year", f"{number(float(best['co2_kg_year']), 1)} kg")

    cost_columns = ["filter_cost_year", "energy_cost_year", "labor_disposal_cost_year"]
    melted = summaries.melt(
        id_vars="scenario",
        value_vars=cost_columns,
        var_name="Cost item",
        value_name="Value",
    )
    melted["Display value"] = melted["Value"].apply(lambda value: compact_value(value))
    fig_tco = px.bar(
        melted,
        x="scenario",
        y="Value",
        color="Cost item",
        text="Display value",
        title="TCO Comparison",
        labels={"Value": f"Cost ({currency})", "scenario": "Scenario"},
        color_discrete_sequence=CHART_COLORS,
    )
    apply_bar_value_style(fig_tco)

    selected = st.selectbox("Cost breakdown scenario", summaries["scenario"].tolist())
    selected_summary = summaries[summaries["scenario"] == selected].iloc[0]
    breakdown = pd.DataFrame(
        {
            "Cost item": ["Filter", "Energy", "Labor/disposal"],
            "Value": [
                selected_summary["filter_cost_year"],
                selected_summary["energy_cost_year"],
                selected_summary["labor_disposal_cost_year"],
            ],
        }
    )
    fig_breakdown = px.pie(
        breakdown,
        names="Cost item",
        values="Value",
        hole=0.45,
        title=f"Cost Breakdown - {selected}",
        color_discrete_sequence=CHART_COLORS,
    )
    fig_breakdown.update_traces(
        texttemplate="%{label}<br>%{value:,.0f}<br>%{percent}",
        textposition="inside",
        textfont_size=11,
    )
    fig_breakdown.update_layout(
        paper_bgcolor="#fffaf0",
        font={"color": "#172033", "size": 12},
        title_font={"size": 16, "color": "#172033"},
        margin={"l": 24, "r": 24, "t": 56, "b": 48},
        legend_title_text="",
    )

    st.markdown('<div class="section-title">Cost Analysis</div>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns(2)
    chart_left.plotly_chart(fig_tco, width="stretch")
    chart_right.plotly_chart(fig_breakdown, width="stretch")

    fig_stage = px.bar(
        stages,
        x="scenario",
        y="tco_year",
        color="stage",
        text=stages["tco_year"].apply(lambda value: compact_value(value)),
        barmode="stack",
        title="TCO/year by Scenario and Stage",
        labels={
            "tco_year": f"TCO/year ({currency})",
            "scenario": "Scenario",
            "stage": "Filter Stage",
        },
        color_discrete_sequence=CHART_COLORS,
    )
    apply_bar_value_style(fig_stage)
    fig_life = px.bar(
        stages,
        x="stage",
        y="life_days",
        color="scenario",
        text=stages["life_days"].apply(lambda value: compact_value(value, " d")),
        barmode="group",
        title="Filter Life by Stage",
        labels={"life_days": "Days", "stage": "Stage"},
        color_discrete_sequence=CHART_COLORS,
    )
    apply_bar_value_style(fig_life)
    st.markdown('<div class="section-title">Stage Performance</div>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns(2)
    chart_left.plotly_chart(fig_stage, width="stretch")
    chart_right.plotly_chart(fig_life, width="stretch")

    fig_energy = px.bar(
        summaries,
        x="scenario",
        y="energy_cost_year",
        text=summaries["energy_cost_year"].apply(lambda value: compact_value(value)),
        title="Energy Cost by Scenario",
        labels={"energy_cost_year": f"Energy cost ({currency})", "scenario": "Scenario"},
        color_discrete_sequence=["#0f9f8f"],
    )
    apply_bar_value_style(fig_energy)
    fig_co2 = px.bar(
        summaries,
        x="scenario",
        y="co2_kg_year",
        text=summaries["co2_kg_year"].apply(lambda value: compact_value(value, " kg")),
        title="CO2 Emission by Scenario",
        labels={"co2_kg_year": "kgCO2/year", "scenario": "Scenario"},
        color_discrete_sequence=["#d99a2b"],
    )
    apply_bar_value_style(fig_co2)
    st.markdown('<div class="section-title">Energy and Emissions</div>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns(2)
    chart_left.plotly_chart(fig_energy, width="stretch")
    chart_right.plotly_chart(fig_co2, width="stretch")
