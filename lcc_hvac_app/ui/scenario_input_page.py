from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd
import streamlit as st

from lcc_hvac_app.engine.eurovent import (
    calculate_eurovent_average_dp,
    default_mx_for_iso_group,
)
from lcc_hvac_app.engine.efficiency import DEFAULT_OUTDOOR_ENVIRONMENT, effective_mass_efficiency
from lcc_hvac_app.engine.models import FilterDatabaseRecord, FilterStage, Scenario


STAGE_OPTIONS = [
    "Pre-filter",
    "Medium-filter",
    "Fine-filter",
    "Final-filter",
    "HEPA",
    "ULPA",
    "Carbon / Odor",
]
ISO_GROUP_OPTIONS = ["ISO ePM1", "ISO ePM2.5", "ISO ePM10", "ISO Coarse"]


def _blank_stage() -> FilterStage:
    return FilterStage(
        stage="Pre-filter",
        qty_per_ahu=1.0,
        dhc_g=100.0,
        mass_efficiency=0.5,
        avg_dp_pa=50.0,
        price_vnd_filter=0.0,
    )


def _field_key(scenario_name: str, row_index: int, field_name: str, key_prefix: str | None = None) -> str:
    nonce = st.session_state.get("editor_nonce", "default")
    safe_name = (key_prefix or scenario_name).replace("/", "_").replace(" ", "_")
    return f"{nonce}_{safe_name}_{row_index}_{field_name}"


def _default_eurovent_curve(avg_dp_pa: float) -> list[dict[str, float]]:
    start_dp = max(avg_dp_pa * 0.9, 0.0)
    return [
        {"dust_fed_g": 0.0, "pressure_drop_pa": start_dp},
        {"dust_fed_g": 50.0, "pressure_drop_pa": avg_dp_pa},
        {"dust_fed_g": 100.0, "pressure_drop_pa": avg_dp_pa * 1.08},
        {"dust_fed_g": 150.0, "pressure_drop_pa": avg_dp_pa * 1.16},
        {"dust_fed_g": 200.0, "pressure_drop_pa": avg_dp_pa * 1.25},
    ]


def _curve_to_dataframe(curve: list[dict[str, float]], avg_dp_pa: float) -> pd.DataFrame:
    rows = curve or _default_eurovent_curve(avg_dp_pa)
    return pd.DataFrame(
        [
            {
                "Dust fed mi (g)": row.get("dust_fed_g", 0.0),
                "Pressure drop dPi (Pa)": row.get("pressure_drop_pa", 0.0),
            }
            for row in rows
        ]
    )


def _dataframe_to_curve(dataframe: pd.DataFrame) -> list[dict[str, float]]:
    curve: list[dict[str, float]] = []
    for _, row in dataframe.fillna("").iterrows():
        dust = _to_float(row.get("Dust fed mi (g)"))
        dp = _to_float(row.get("Pressure drop dPi (Pa)"))
        if dust is None and dp is None:
            continue
        curve.append(
            {
                "dust_fed_g": dust or 0.0,
                "pressure_drop_pa": dp or 0.0,
            }
        )
    return curve


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def _calculate_media_area_m2(width_mm: float, height_mm: float) -> float:
    if width_mm <= 0 or height_mm <= 0:
        return 0.0
    return round(width_mm * height_mm / 1_000_000, 4)


def _format_efficiency(value: float) -> str:
    efficiency = value / 100.0 if value > 1 else value
    return f"{efficiency * 100:,.1f}%"


def _filter_label(record: FilterDatabaseRecord) -> str:
    dimensions = ""
    if record.width_mm and record.height_mm:
        dimensions = f"{record.width_mm:,.0f}x{record.height_mm:,.0f} mm"
    parts = [
        record.filter_id,
        record.model,
        record.stage,
        dimensions,
    ]
    return " | ".join(part for part in parts if str(part).strip())


def _database_lookup(
    filter_database: list[FilterDatabaseRecord],
) -> dict[str, FilterDatabaseRecord]:
    return {
        record.filter_id: record
        for record in filter_database
        if record.filter_id.strip()
    }


def _apply_filter_record_to_session(
    record: FilterDatabaseRecord,
    scenario_name: str,
    row_index: int,
    key_prefix: str | None,
) -> None:
    field_values = {
        "stage": record.stage,
        "qty_per_ahu": record.qty_per_ahu,
        "width_mm": record.width_mm,
        "height_mm": record.height_mm,
        "media_area_m2": record.media_area_m2,
        "dhc_g": record.dhc_g,
        "mass_efficiency": record.mass_efficiency,
        "avg_dp_pa": record.avg_dp_pa,
        "price_vnd_filter": record.price_vnd_filter,
    }
    for field_name, value in field_values.items():
        st.session_state[_field_key(scenario_name, row_index, field_name, key_prefix)] = value


def _apply_selected_filter_id_to_session(
    filter_key: str,
    filter_lookup: dict[str, FilterDatabaseRecord],
    scenario_name: str,
    row_index: int,
    key_prefix: str | None,
) -> None:
    selected_filter_id = st.session_state.get(filter_key)
    record = filter_lookup.get(selected_filter_id)
    if record is not None:
        _apply_filter_record_to_session(record, scenario_name, row_index, key_prefix)


def _record_to_stage(
    record: FilterDatabaseRecord,
    outdoor_environment: str = DEFAULT_OUTDOOR_ENVIRONMENT,
) -> FilterStage:
    mass_efficiency, _source = effective_mass_efficiency(
        record.mass_efficiency,
        getattr(record, "epm1_percent", 0.0),
        getattr(record, "epm25_percent", 0.0),
        getattr(record, "epm10_percent", 0.0),
        getattr(record, "coarse_percent", 0.0),
        outdoor_environment,
        record.filter_class,
    )
    return FilterStage(
        stage=record.stage,
        qty_per_ahu=record.qty_per_ahu,
        dhc_g=record.dhc_g,
        mass_efficiency=mass_efficiency,
        avg_dp_pa=record.avg_dp_pa,
        price_vnd_filter=record.price_vnd_filter,
        width_mm=record.width_mm,
        height_mm=record.height_mm,
        media_area_m2=record.media_area_m2 or _calculate_media_area_m2(
            record.width_mm,
            record.height_mm,
        ),
        filter_id=record.filter_id,
    )


def _default_filter_index(
    filter_options: list[str],
    filter_lookup: dict[str, FilterDatabaseRecord],
    stage: FilterStage,
) -> int:
    current_filter_id = getattr(stage, "filter_id", "")
    if current_filter_id in filter_options:
        return filter_options.index(current_filter_id)
    for index, filter_id in enumerate(filter_options):
        if filter_lookup[filter_id].stage == stage.stage:
            return index
    return 0


def render_eurovent_dp_calculator(
    stage: FilterStage,
    index: int,
    key_prefix: str | None,
    avg_dp_key: str,
) -> tuple[str, float, list[dict[str, float]]]:
    safe_prefix = key_prefix or stage.stage.replace("/", "_").replace(" ", "_")
    stored_iso_group = getattr(stage, "eurovent_iso_group", "ISO ePM1")
    iso_group = stored_iso_group if stored_iso_group in ISO_GROUP_OPTIONS else "ISO ePM1"
    eurovent_curve = getattr(stage, "eurovent_curve", [])
    eurovent_mx_g = getattr(stage, "eurovent_mx_g", default_mx_for_iso_group(iso_group))
    curve_df = _curve_to_dataframe(eurovent_curve, float(stage.avg_dp_pa))

    with st.expander("Eurovent 4/21 Average DP Calculator", expanded=False):
        st.caption(
            "Uses the Excel Eurovent_DP_Calc method: segment average DP x dust increment, summed to Mx and divided by Mx."
        )
        input_col, result_col = st.columns([2, 1])
        with input_col:
            selected_iso = st.selectbox(
                "ISO Group",
                ISO_GROUP_OPTIONS,
                index=ISO_GROUP_OPTIONS.index(iso_group),
                key=f"{safe_prefix}_{index}_eurovent_iso",
            )
            mx_g = st.number_input(
                "Mx used for calculation (g)",
                min_value=0.01,
                value=float(eurovent_mx_g or default_mx_for_iso_group(selected_iso)),
                step=10.0,
                help="Excel default: ISO ePM1=200g, ISO ePM2.5=250g, ISO ePM10=400g.",
                key=f"{safe_prefix}_{index}_eurovent_mx",
            )
        with result_col:
            st.metric("Default Mx", f"{default_mx_for_iso_group(selected_iso):,.0f} g")

        edited_curve = st.data_editor(
            curve_df,
            num_rows="dynamic",
            hide_index=True,
            width="stretch",
            key=f"{safe_prefix}_{index}_eurovent_curve",
            column_config={
                "Dust fed mi (g)": st.column_config.NumberColumn(
                    "Dust fed mi (g)",
                    min_value=0.0,
                    step=10.0,
                ),
                "Pressure drop dPi (Pa)": st.column_config.NumberColumn(
                    "Pressure drop dPi (Pa)",
                    min_value=0.0,
                    step=1.0,
                ),
            },
        )
        curve = _dataframe_to_curve(edited_curve)

        try:
            result = calculate_eurovent_average_dp(curve, mx_g)
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            kpi_col1.metric("Eurovent Avg DP", f"{result.average_dp_pa:,.2f} Pa")
            kpi_col2.metric("Covered dust", f"{result.covered_dust_g:,.1f} g")
            kpi_col3.metric("Weighted DP sum", f"{result.weighted_dp_sum:,.1f}")
            if result.covered_dust_g < mx_g:
                st.warning(
                    "The curve does not reach Mx. The result follows the Excel formula, but add more test points for a more complete result."
                )
            if st.button(
                "Apply Eurovent Avg DP to this stage",
                key=f"{safe_prefix}_{index}_apply_eurovent_dp",
                width="stretch",
            ):
                st.session_state[avg_dp_key] = float(result.average_dp_pa)
                st.success(f"Applied {result.average_dp_pa:,.2f} Pa to Average Pressure Drop.")

            detail = pd.DataFrame([asdict(segment) for segment in result.segments])
            detail = detail.rename(
                columns={
                    "step": "Step",
                    "previous_dust_fed_g": "Previous dust (g)",
                    "dust_fed_g": "Dust fed mi (g)",
                    "previous_dp_pa": "Previous DP (Pa)",
                    "dp_pa": "DPi (Pa)",
                    "dust_increment_g": "Dust increment dmi (g)",
                    "segment_avg_dp_pa": "Segment avg DP (Pa)",
                    "weighted_dp_g_pa": "Weighted DP x dmi",
                    "used_to_mx": "Use to Mx?",
                }
            )
            st.dataframe(detail, width="stretch", hide_index=True)
        except ValueError as exc:
            st.info(f"Eurovent DP cannot be calculated yet: {exc}")

    return selected_iso, float(mx_g), curve


def render_scenario_editor(
    scenario: Scenario,
    key_prefix: str | None = None,
    filter_database: list[FilterDatabaseRecord] | None = None,
    outdoor_environment: str = DEFAULT_OUTDOOR_ENVIRONMENT,
) -> Scenario:
    st.markdown("**Filter Stages**")
    st.caption("Choose filters from Filter Data. Scenario calculations use the saved database values.")

    stages = list(scenario.stages)
    add_key = f"add_{key_prefix or scenario.name}"
    edited_stages: list[FilterStage] = []
    database_records = filter_database or []
    filter_lookup = _database_lookup(database_records)
    if not filter_lookup:
        st.info("No Filter ID is available yet. Add filters in the Filter Data section, then return here to build scenarios.")
        return Scenario(scenario.name, [])

    if st.button("Add Stage", key=add_key, width="stretch"):
        stages.append(
            _record_to_stage(filter_lookup[next(iter(filter_lookup))], outdoor_environment)
        )

    for index, stage in enumerate(stages):
        with st.container(border=True):
            title_col, remove_col = st.columns([5, 1])
            title_col.markdown(f"**Stage {index + 1}: {stage.stage}**")
            remove = remove_col.button(
                "Remove",
                key=_field_key(scenario.name, index, "remove", key_prefix),
                width="stretch",
            )
            if remove:
                continue

            filter_options = list(filter_lookup.keys())
            filter_index = _default_filter_index(filter_options, filter_lookup, stage)
            filter_key = _field_key(scenario.name, index, "filter_id", key_prefix)
            selected_filter_id = st.selectbox(
                "Select Filter ID from Filter Data",
                options=filter_options,
                index=filter_index,
                format_func=lambda value: _filter_label(filter_lookup[value]),
                key=filter_key,
                help="Choose a filter from the Filter Data page. Its saved parameters are used for this scenario.",
            )
            selected_record = filter_lookup[selected_filter_id]
            st.caption("Values below are read from Filter Data. Edit the database record if you need to change them.")

            info_cols = st.columns(4)
            info_cols[0].metric("Stage", selected_record.stage or "-")
            info_cols[1].metric("Model", selected_record.model or "-")
            info_cols[2].metric("ISO Class", selected_record.filter_class or "-")
            info_cols[3].metric(
                "Size",
                f"{selected_record.width_mm:,.0f} x {selected_record.height_mm:,.0f} mm"
                if selected_record.width_mm and selected_record.height_mm
                else "-",
            )

            value_cols = st.columns(6)
            effective_efficiency, efficiency_source = effective_mass_efficiency(
                selected_record.mass_efficiency,
                getattr(selected_record, "epm1_percent", 0.0),
                getattr(selected_record, "epm25_percent", 0.0),
                getattr(selected_record, "epm10_percent", 0.0),
                getattr(selected_record, "coarse_percent", 0.0),
                outdoor_environment,
                selected_record.filter_class,
            )
            value_cols[0].metric("Qty/AHU", f"{selected_record.qty_per_ahu:,.0f}")
            value_cols[1].metric("DHC", f"{selected_record.dhc_g:,.0f} g")
            value_cols[2].metric("Mass Eff.", _format_efficiency(effective_efficiency))
            value_cols[3].metric("Avg DP", f"{selected_record.avg_dp_pa:,.0f} Pa")
            value_cols[4].metric("Final DP", f"{selected_record.final_dp_pa:,.0f} Pa")
            value_cols[5].metric("Price", f"{selected_record.price_vnd_filter:,.0f}")
            st.caption(f"Mass efficiency source: {efficiency_source}")

            geometry_cols = st.columns(3)
            media_area = selected_record.media_area_m2 or _calculate_media_area_m2(
                selected_record.width_mm,
                selected_record.height_mm,
            )
            geometry_cols[0].metric("Width", f"{selected_record.width_mm:,.0f} mm")
            geometry_cols[1].metric("Height", f"{selected_record.height_mm:,.0f} mm")
            geometry_cols[2].metric("Media area/filter", f"{media_area:,.4f} m2")

            edited_stages.append(_record_to_stage(selected_record, outdoor_environment))

    return Scenario(scenario.name, edited_stages)


def copy_scenario(source: Scenario, target_name: str) -> Scenario:
    return Scenario(
        target_name,
        [
            FilterStage(
                stage=stage.stage,
                qty_per_ahu=stage.qty_per_ahu,
                dhc_g=stage.dhc_g,
                mass_efficiency=stage.mass_efficiency,
                avg_dp_pa=stage.avg_dp_pa,
                price_vnd_filter=stage.price_vnd_filter,
                width_mm=getattr(stage, "width_mm", 0.0),
                height_mm=getattr(stage, "height_mm", 0.0),
                media_area_m2=getattr(stage, "media_area_m2", 0.0),
                filter_id=getattr(stage, "filter_id", ""),
                eurovent_iso_group=getattr(stage, "eurovent_iso_group", "ISO ePM1"),
                eurovent_mx_g=getattr(stage, "eurovent_mx_g", 200.0),
                eurovent_curve=[
                    dict(point) for point in getattr(stage, "eurovent_curve", [])
                ],
            )
            for stage in source.stages
        ],
    )
