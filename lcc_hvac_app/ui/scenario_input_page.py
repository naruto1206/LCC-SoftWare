from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd
import streamlit as st

from lcc_hvac_app.engine.eurovent import (
    calculate_eurovent_average_dp,
    default_mx_for_iso_group,
)
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
            use_container_width=True,
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
                use_container_width=True,
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
            st.dataframe(detail, use_container_width=True, hide_index=True)
        except ValueError as exc:
            st.info(f"Eurovent DP cannot be calculated yet: {exc}")

    return selected_iso, float(mx_g), curve


def render_scenario_editor(
    scenario: Scenario,
    key_prefix: str | None = None,
    filter_database: list[FilterDatabaseRecord] | None = None,
) -> Scenario:
    st.markdown("**Filter Stages**")
    st.caption("Mass efficiency accepts decimal values such as 0.85 or percent values such as 85.")

    stages = list(scenario.stages)
    add_key = f"add_{key_prefix or scenario.name}"
    if st.button("Add Stage", key=add_key, use_container_width=True):
        stages.append(_blank_stage())

    edited_stages: list[FilterStage] = []
    database_records = filter_database or []
    filter_lookup = _database_lookup(database_records)
    if not filter_lookup:
        st.info("No Filter ID is available yet. Add filters in the Filter Data section, then return here to select them.")
    for index, stage in enumerate(stages):
        with st.container(border=True):
            title_col, remove_col = st.columns([5, 1])
            title_col.markdown(f"**Stage {index + 1}: {stage.stage}**")
            remove = remove_col.button(
                "Remove",
                key=_field_key(scenario.name, index, "remove", key_prefix),
                use_container_width=True,
            )
            if remove:
                continue

            filter_options = ["Manual input"] + list(filter_lookup.keys())
            current_filter_id = getattr(stage, "filter_id", "")
            filter_index = (
                filter_options.index(current_filter_id)
                if current_filter_id in filter_options
                else 0
            )
            filter_key = _field_key(scenario.name, index, "filter_id", key_prefix)
            selected_filter_id = st.selectbox(
                "Select Filter ID from Filter Data",
                options=filter_options,
                index=filter_index,
                format_func=lambda value: (
                    "Manual input"
                    if value == "Manual input"
                    else _filter_label(filter_lookup[value])
                ),
                key=filter_key,
                help="Choose a filter from the Filter Data page. Its parameters load into the editable inputs below.",
                on_change=_apply_selected_filter_id_to_session,
                args=(filter_key, filter_lookup, scenario.name, index, key_prefix),
            )
            selected_record = filter_lookup.get(selected_filter_id)
            if selected_record is not None:
                st.caption(
                    "Selected filter values are loaded into the inputs below. You can still adjust any parameter for this scenario."
                )
                info_cols = st.columns(7)
                info_cols[0].metric("Model", selected_record.model or "-")
                info_cols[1].metric("ISO Class", selected_record.filter_class or "-")
                info_cols[2].metric(
                    "Size",
                    f"{selected_record.width_mm:,.0f} x {selected_record.height_mm:,.0f} mm"
                    if selected_record.width_mm and selected_record.height_mm
                    else "-",
                )
                info_cols[3].metric("Qty/AHU", f"{selected_record.qty_per_ahu:,.0f}")
                info_cols[4].metric("DHC", f"{selected_record.dhc_g:,.0f} g")
                info_cols[5].metric("Avg DP", f"{selected_record.avg_dp_pa:,.0f} Pa")
                info_cols[6].metric("Price", f"{selected_record.price_vnd_filter:,.0f}")
                if st.button(
                    "Reload parameters from selected filter",
                    key=_field_key(scenario.name, index, "apply_filter", key_prefix),
                    use_container_width=True,
                ):
                    _apply_filter_record_to_session(
                        selected_record,
                        scenario.name,
                        index,
                        key_prefix,
                    )
                    st.success(f"Applied {selected_record.filter_id} to this stage.")

            col1, col2, col3 = st.columns(3)
            stage_options = list(STAGE_OPTIONS)
            if stage.stage and stage.stage not in stage_options:
                stage_options.append(stage.stage)
            if selected_record is not None and selected_record.stage not in stage_options:
                stage_options.append(selected_record.stage)
            stage_name = col1.selectbox(
                "Stage",
                options=stage_options,
                index=stage_options.index(stage.stage) if stage.stage in stage_options else 0,
                key=_field_key(scenario.name, index, "stage", key_prefix),
            )
            qty_per_ahu = col2.number_input(
                "Quantity per AHU",
                min_value=0.0,
                value=float(stage.qty_per_ahu),
                step=1.0,
                key=_field_key(scenario.name, index, "qty_per_ahu", key_prefix),
            )
            dhc_g = col3.number_input(
                "Dust Holding Capacity (g)",
                min_value=0.0,
                value=float(stage.dhc_g),
                step=50.0,
                key=_field_key(scenario.name, index, "dhc_g", key_prefix),
            )

            col4, col5, col6 = st.columns(3)
            avg_dp_key = _field_key(scenario.name, index, "avg_dp_pa", key_prefix)
            eurovent_iso_group, eurovent_mx_g, eurovent_curve = render_eurovent_dp_calculator(
                stage,
                index,
                key_prefix,
                avg_dp_key,
            )
            mass_efficiency = col4.number_input(
                "Mass Efficiency",
                min_value=0.0,
                value=float(stage.mass_efficiency),
                step=0.01,
                key=_field_key(scenario.name, index, "mass_efficiency", key_prefix),
            )
            avg_dp_pa = col5.number_input(
                "Average Pressure Drop (Pa)",
                min_value=0.0,
                value=float(stage.avg_dp_pa),
                step=5.0,
                key=avg_dp_key,
            )
            price_vnd_filter = col6.number_input(
                "Price per Filter",
                min_value=0.0,
                value=float(stage.price_vnd_filter),
                step=10000.0,
                key=_field_key(scenario.name, index, "price_vnd_filter", key_prefix),
            )

            with st.expander("Geometry check", expanded=False):
                geo_col1, geo_col2, geo_col3 = st.columns(3)
                width_mm = geo_col1.number_input(
                    "Width (mm)",
                    min_value=0.0,
                    value=float(getattr(stage, "width_mm", 0.0)),
                    step=1.0,
                    key=_field_key(scenario.name, index, "width_mm", key_prefix),
                )
                height_mm = geo_col2.number_input(
                    "Height (mm)",
                    min_value=0.0,
                    value=float(getattr(stage, "height_mm", 0.0)),
                    step=1.0,
                    key=_field_key(scenario.name, index, "height_mm", key_prefix),
                )
                media_area_m2 = _calculate_media_area_m2(width_mm, height_mm)
                geo_col3.number_input(
                    "Media area/filter (m2)",
                    min_value=0.0,
                    value=media_area_m2,
                    step=0.01,
                    disabled=True,
                    help="Calculated from Width x Height / 1,000,000 for app consistency.",
                )

            if stage_name.strip():
                edited_stages.append(
                    FilterStage(
                        stage=stage_name.strip(),
                        qty_per_ahu=qty_per_ahu,
                        dhc_g=dhc_g,
                        mass_efficiency=mass_efficiency,
                        avg_dp_pa=avg_dp_pa,
                        price_vnd_filter=price_vnd_filter,
                        width_mm=width_mm,
                        height_mm=height_mm,
                        media_area_m2=media_area_m2,
                        filter_id="" if selected_filter_id == "Manual input" else selected_filter_id,
                        eurovent_iso_group=eurovent_iso_group,
                        eurovent_mx_g=eurovent_mx_g,
                        eurovent_curve=eurovent_curve,
                    )
                )

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
