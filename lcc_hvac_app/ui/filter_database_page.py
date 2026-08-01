from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
import streamlit as st

from lcc_hvac_app.engine.models import FilterDatabaseRecord
from lcc_hvac_app.project_io.filter_database_store import save_filter_database


DATABASE_COLUMNS = [
    "filter_id",
    "supplier",
    "filter_type",
    "stage",
    "model",
    "size",
    "filter_class",
    "dhc_g",
    "initial_dp_pa",
    "avg_dp_pa",
    "final_dp_pa",
    "mass_efficiency",
    "price_vnd_filter",
    "notes",
]

DISPLAY_COLUMNS = {
    "filter_id": "Filter ID",
    "supplier": "Supplier",
    "filter_type": "Filter Type",
    "stage": "Stage",
    "model": "Model",
    "size": "Size",
    "filter_class": "ISO Class",
    "dhc_g": "DHC (g)",
    "initial_dp_pa": "Initial DP (Pa)",
    "avg_dp_pa": "Avg DP (Pa)",
    "final_dp_pa": "Final DP (Pa)",
    "mass_efficiency": "Mass Efficiency",
    "price_vnd_filter": "Price/filter",
    "notes": "Notes",
}

STAGE_OPTIONS = [
    "",
    "Pre-filter",
    "Medium-filter",
    "Fine-filter",
    "Final-filter",
    "HEPA",
    "ULPA",
    "Carbon / Odor",
]

ISO_CLASS_OPTIONS = [
    "",
    "ISO Coarse",
    "ISO Coarse 30%",
    "ISO Coarse 45%",
    "ISO Coarse 60%",
    "ISO Coarse 80%",
    "ISO ePM10 50%",
    "ISO ePM10 60%",
    "ISO ePM10 70%",
    "ISO ePM10 80%",
    "ISO ePM10 90%",
    "ISO ePM2.5 50%",
    "ISO ePM2.5 60%",
    "ISO ePM2.5 70%",
    "ISO ePM2.5 80%",
    "ISO ePM2.5 90%",
    "ISO ePM1 50%",
    "ISO ePM1 60%",
    "ISO ePM1 70%",
    "ISO ePM1 80%",
    "ISO ePM1 90%",
    "G3 / ISO Coarse",
    "G4 / ISO Coarse",
    "M5 / ISO ePM10",
    "M6 / ISO ePM10",
    "F7 / ISO ePM2.5",
    "F8 / ISO ePM1",
    "F9 / ISO ePM1",
    "E10",
    "E11",
    "E12",
    "H13",
    "H14",
    "U15",
    "U16",
    "U17",
]

COLUMN_ALIASES = {
    "filter_id": ["filter id", "id", "code", "filter code", "product code"],
    "supplier": ["supplier", "brand", "manufacturer", "maker"],
    "filter_type": ["filter type", "type", "product type"],
    "stage": ["stage", "filter stage", "level"],
    "model": ["model", "filter model", "product", "item"],
    "size": ["size", "dimension", "dimensions"],
    "filter_class": ["class", "grade", "filter class", "en class", "iso class", "ISO Class"],
    "dhc_g": ["dhc", "dhc (g)", "dust holding capacity", "dust holding capacity (g)"],
    "initial_dp_pa": ["initial dp", "initial dp (pa)", "initial pressure drop"],
    "avg_dp_pa": ["avg dp", "avg dp (pa)", "average dp", "average pressure drop"],
    "final_dp_pa": ["final dp", "final dp (pa)", "final pressure drop"],
    "mass_efficiency": ["mass efficiency", "mass eff.", "efficiency", "eff"],
    "price_vnd_filter": ["price/filter", "price", "unit price", "filter price"],
    "notes": ["notes", "note", "remark", "remarks"],
}


def _choice_options(defaults: list[str], dataframe: pd.DataFrame, display_column: str) -> list[str]:
    options = list(defaults)
    if display_column in dataframe.columns:
        for value in dataframe[display_column].dropna():
            text = str(value).strip()
            if text and text not in options:
                options.append(text)
    return options


def records_to_dataframe(records: list[FilterDatabaseRecord]) -> pd.DataFrame:
    data = [{column: getattr(record, column) for column in DATABASE_COLUMNS} for record in records]
    return pd.DataFrame(data, columns=DATABASE_COLUMNS).rename(columns=DISPLAY_COLUMNS)


def empty_display_row() -> dict[str, Any]:
    return {
        column: 0.0
        if column
        in {
            "DHC (g)",
            "Initial DP (Pa)",
            "Avg DP (Pa)",
            "Final DP (Pa)",
            "Mass Efficiency",
            "Price/filter",
        }
        else ""
        for column in DISPLAY_COLUMNS.values()
    }


def normalize_display_dataframe(dataframe: pd.DataFrame | None) -> pd.DataFrame:
    if dataframe is None:
        return pd.DataFrame(columns=list(DISPLAY_COLUMNS.values()))
    normalized = dataframe.copy()
    if "Class" in normalized.columns and "ISO Class" not in normalized.columns:
        normalized = normalized.rename(columns={"Class": "ISO Class"})
    return normalized.reindex(columns=list(DISPLAY_COLUMNS.values()), fill_value="")


def sync_filter_database_editor(editor_key: str) -> None:
    editor_state = st.session_state.get(editor_key, {})
    current = normalize_display_dataframe(st.session_state.get("filter_database_data"))
    if not isinstance(editor_state, dict):
        return

    for row_index, changes in editor_state.get("edited_rows", {}).items():
        index = int(row_index)
        if index >= len(current):
            continue
        for column_name, value in changes.items():
            if column_name in current.columns:
                current.at[index, column_name] = value

    added_rows = editor_state.get("added_rows", [])
    if added_rows:
        current = pd.concat(
            [current, normalize_display_dataframe(pd.DataFrame(added_rows))],
            ignore_index=True,
        )

    deleted_rows = sorted(
        [int(index) for index in editor_state.get("deleted_rows", [])],
        reverse=True,
    )
    for index in deleted_rows:
        if index < len(current):
            current = current.drop(current.index[index])

    st.session_state.filter_database_data = normalize_display_dataframe(
        current.reset_index(drop=True)
    )


def upsert_filter_database_row(row: dict[str, Any]) -> None:
    current = normalize_display_dataframe(st.session_state.get("filter_database_data"))
    filter_id = str(row.get("Filter ID", "")).strip()
    if not filter_id:
        st.warning("Filter ID is required before adding a filter record.")
        return

    new_row = normalize_display_dataframe(pd.DataFrame([row]))
    existing_matches = current["Filter ID"].astype(str).str.strip() == filter_id
    if existing_matches.any():
        current.loc[existing_matches, list(DISPLAY_COLUMNS.values())] = new_row.iloc[0].values
        st.success(f"Updated filter {filter_id}.")
    else:
        current = pd.concat([current, new_row], ignore_index=True)
        st.success(f"Added filter {filter_id}.")
    st.session_state.filter_database_data = normalize_display_dataframe(current)
    persist_filter_database_dataframe(current)
    st.session_state.filter_database_nonce = st.session_state.get(
        "filter_database_nonce", 0
    ) + 1


def _row_value(row: pd.Series | None, column: str, default: Any = "") -> Any:
    if row is None:
        return default
    value = row.get(column, default)
    if pd.isna(value):
        return default
    return value


def persist_filter_database_dataframe(dataframe: pd.DataFrame) -> None:
    try:
        save_filter_database(dataframe_to_records(normalize_display_dataframe(dataframe)))
    except OSError as exc:
        st.warning(f"Filter database was updated for this session, but could not be saved to disk: {exc}")


def remove_filter_database_rows(
    dataframe: pd.DataFrame,
    filter_ids: list[str],
) -> pd.DataFrame:
    normalized = normalize_display_dataframe(dataframe)
    ids_to_delete = {str(filter_id).strip() for filter_id in filter_ids if str(filter_id).strip()}
    if not ids_to_delete or "Filter ID" not in normalized.columns:
        return normalized
    keep_mask = ~normalized["Filter ID"].astype(str).str.strip().isin(ids_to_delete)
    return normalize_display_dataframe(normalized.loc[keep_mask].reset_index(drop=True))


def _option_index(options: list[str], value: Any) -> int:
    text = str(value or "").strip()
    return options.index(text) if text in options else 0


def _missing_filter_record_fields(row: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    required_text_fields = [
        "Filter ID",
        "Supplier",
        "Filter Type",
        "Stage",
        "Model",
        "Size",
        "ISO Class",
    ]
    required_positive_fields = [
        "DHC (g)",
        "Initial DP (Pa)",
        "Avg DP (Pa)",
        "Final DP (Pa)",
        "Mass Efficiency",
        "Price/filter",
    ]

    for field_name in required_text_fields:
        if not str(row.get(field_name, "")).strip():
            missing.append(field_name)

    for field_name in required_positive_fields:
        if _to_float(row.get(field_name, 0)) <= 0:
            missing.append(field_name)

    return missing


def render_quick_add_filter_form(current_df: pd.DataFrame) -> None:
    filter_ids = [
        str(value).strip()
        for value in current_df["Filter ID"].fillna("").tolist()
        if str(value).strip()
    ]
    selected_existing = st.selectbox(
        "Edit existing filter",
        ["Create new filter"] + filter_ids,
        help="Choose an existing Filter ID to update it, or create a new filter.",
        key="filter_record_to_edit",
    )
    selected_row = None
    if selected_existing != "Create new filter":
        matches = current_df[current_df["Filter ID"].astype(str).str.strip() == selected_existing]
        if not matches.empty:
            selected_row = matches.iloc[0]
    form_key = selected_existing.replace(" ", "_").replace("/", "_").replace("\\", "_")

    with st.expander("Add or update one filter record", expanded=True):
        st.caption("Complete all required fields before saving. Notes are optional.")
        col1, col2, col3 = st.columns(3)
        filter_id = col1.text_input(
            "Filter ID",
            value=str(_row_value(selected_row, "Filter ID")),
            key=f"filter_id_{form_key}",
        )
        supplier = col2.text_input(
            "Supplier",
            value=str(_row_value(selected_row, "Supplier")),
            key=f"supplier_{form_key}",
        )
        filter_type = col3.text_input(
            "Filter Type",
            value=str(_row_value(selected_row, "Filter Type")),
            key=f"filter_type_{form_key}",
        )

        col4, col5, col6 = st.columns(3)
        stage = col4.selectbox(
            "Stage",
            STAGE_OPTIONS,
            index=_option_index(STAGE_OPTIONS, _row_value(selected_row, "Stage")),
            key=f"stage_{form_key}",
        )
        model = col5.text_input(
            "Model",
            value=str(_row_value(selected_row, "Model")),
            key=f"model_{form_key}",
        )
        size = col6.text_input(
            "Size",
            value=str(_row_value(selected_row, "Size")),
            key=f"size_{form_key}",
        )

        col7, col8, col9 = st.columns(3)
        iso_class = col7.selectbox(
            "ISO Class",
            ISO_CLASS_OPTIONS,
            index=_option_index(ISO_CLASS_OPTIONS, _row_value(selected_row, "ISO Class")),
            key=f"iso_class_{form_key}",
        )
        dhc_g = col8.number_input(
            "DHC (g)",
            min_value=0.0,
            value=float(_row_value(selected_row, "DHC (g)", 0.0)),
            step=50.0,
            key=f"dhc_g_{form_key}",
        )
        mass_efficiency = col9.number_input(
            "Mass Efficiency",
            min_value=0.0,
            value=float(_row_value(selected_row, "Mass Efficiency", 0.0)),
            step=0.01,
            key=f"mass_efficiency_{form_key}",
        )

        col10, col11, col12 = st.columns(3)
        initial_dp = col10.number_input(
            "Initial DP (Pa)",
            min_value=0.0,
            value=float(_row_value(selected_row, "Initial DP (Pa)", 0.0)),
            step=5.0,
            key=f"initial_dp_{form_key}",
        )
        avg_dp = col11.number_input(
            "Avg DP (Pa)",
            min_value=0.0,
            value=float(_row_value(selected_row, "Avg DP (Pa)", 0.0)),
            step=5.0,
            key=f"avg_dp_{form_key}",
        )
        final_dp = col12.number_input(
            "Final DP (Pa)",
            min_value=0.0,
            value=float(_row_value(selected_row, "Final DP (Pa)", 0.0)),
            step=5.0,
            key=f"final_dp_{form_key}",
        )

        col13, col14 = st.columns([1, 2])
        price = col13.number_input(
            "Price/filter",
            min_value=0.0,
            value=float(_row_value(selected_row, "Price/filter", 0.0)),
            step=10000.0,
            key=f"price_{form_key}",
        )
        notes = col14.text_input(
            "Notes",
            value=str(_row_value(selected_row, "Notes")),
            key=f"notes_{form_key}",
        )

        filter_record = {
            "Filter ID": filter_id,
            "Supplier": supplier,
            "Filter Type": filter_type,
            "Stage": stage,
            "Model": model,
            "Size": size,
            "ISO Class": iso_class,
            "DHC (g)": dhc_g,
            "Initial DP (Pa)": initial_dp,
            "Avg DP (Pa)": avg_dp,
            "Final DP (Pa)": final_dp,
            "Mass Efficiency": mass_efficiency,
            "Price/filter": price,
            "Notes": notes,
        }
        missing_fields = _missing_filter_record_fields(filter_record)
        if missing_fields:
            st.info("Please complete: " + ", ".join(missing_fields))

        submitted = st.button(
            "Save filter record",
            use_container_width=True,
            disabled=bool(missing_fields),
        )
        if submitted:
            upsert_filter_database_row(filter_record)
            st.rerun()

    if selected_existing != "Create new filter":
        if st.button("Delete selected filter record", use_container_width=True):
            remaining = current_df[
                current_df["Filter ID"].astype(str).str.strip() != selected_existing
            ].reset_index(drop=True)
            st.session_state.filter_database_data = normalize_display_dataframe(remaining)
            persist_filter_database_dataframe(remaining)
            st.session_state.filter_database_nonce = st.session_state.get(
                "filter_database_nonce", 0
            ) + 1
            st.success(f"Deleted filter {selected_existing}.")
            st.rerun()


def dataframe_to_records(dataframe: pd.DataFrame) -> list[FilterDatabaseRecord]:
    rename_map = {value: key for key, value in DISPLAY_COLUMNS.items()}
    rename_map["Class"] = "filter_class"
    internal = dataframe.rename(columns=rename_map)
    records: list[FilterDatabaseRecord] = []
    for _, row in internal.fillna("").iterrows():
        if not any(str(row.get(column, "")).strip() for column in DATABASE_COLUMNS):
            continue
        records.append(
            FilterDatabaseRecord(
                filter_id=str(row.get("filter_id", "")).strip(),
                supplier=str(row.get("supplier", "")).strip(),
                filter_type=str(row.get("filter_type", "")).strip(),
                stage=str(row.get("stage", "")).strip(),
                model=str(row.get("model", "")).strip(),
                size=str(row.get("size", "")).strip(),
                filter_class=str(row.get("filter_class", "")).strip(),
                dhc_g=_to_float(row.get("dhc_g", 0)),
                initial_dp_pa=_to_float(row.get("initial_dp_pa", 0)),
                avg_dp_pa=_to_float(row.get("avg_dp_pa", 0)),
                final_dp_pa=_to_float(row.get("final_dp_pa", 0)),
                mass_efficiency=_to_float(row.get("mass_efficiency", 0)),
                price_vnd_filter=_to_float(row.get("price_vnd_filter", 0)),
                notes=str(row.get("notes", "")).strip(),
            )
        )
    return records


def _to_float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return 0.0


def _normalize_column_name(name: object) -> str:
    return str(name or "").strip().lower().replace("_", " ")


def normalize_uploaded_database(dataframe: pd.DataFrame) -> pd.DataFrame:
    source = dataframe.dropna(how="all").copy()
    source.columns = [str(column).strip() for column in source.columns]
    normalized = pd.DataFrame(columns=DATABASE_COLUMNS)

    source_lookup = {_normalize_column_name(column): column for column in source.columns}
    for target_column, aliases in COLUMN_ALIASES.items():
        matched_column = None
        for alias in aliases:
            if alias in source_lookup:
                matched_column = source_lookup[alias]
                break
        if matched_column is not None:
            normalized[target_column] = source[matched_column]
        else:
            normalized[target_column] = ""

    for number_column in [
        "dhc_g",
        "initial_dp_pa",
        "avg_dp_pa",
        "final_dp_pa",
        "mass_efficiency",
        "price_vnd_filter",
    ]:
        normalized[number_column] = normalized[number_column].apply(_to_float)

    return normalized.rename(columns=DISPLAY_COLUMNS)


def read_excel_database(uploaded_file: Any, sheet_name: str) -> pd.DataFrame:
    raw = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    return normalize_uploaded_database(raw)


def dataframe_to_excel_bytes(dataframe: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        normalize_display_dataframe(dataframe).to_excel(
            writer,
            index=False,
            sheet_name="Filter_Database",
        )
    return output.getvalue()


def render_filter_record_delete_tools(saved_df: pd.DataFrame) -> pd.DataFrame:
    filter_ids = [
        str(value).strip()
        for value in saved_df["Filter ID"].fillna("").tolist()
        if str(value).strip()
    ]
    if not filter_ids:
        return saved_df

    with st.expander("Delete filter records", expanded=False):
        selected_ids = st.multiselect(
            "Select Filter ID rows to delete",
            filter_ids,
            help="You can select one or many filter records, then delete them together.",
            key="filter_records_to_delete",
        )
        delete_col, count_col = st.columns([1, 2])
        delete_clicked = delete_col.button(
            "Delete selected rows",
            use_container_width=True,
            disabled=not selected_ids,
        )
        count_col.caption(f"{len(selected_ids)} row(s) selected.")
        if delete_clicked:
            remaining = remove_filter_database_rows(saved_df, selected_ids)
            st.session_state.filter_database_data = remaining
            persist_filter_database_dataframe(remaining)
            st.session_state.filter_database_nonce = st.session_state.get(
                "filter_database_nonce", 0
            ) + 1
            st.success(f"Deleted {len(selected_ids)} filter record(s).")
            st.rerun()
    return saved_df


def render_filter_database(records: list[FilterDatabaseRecord]) -> list[FilterDatabaseRecord]:
    st.subheader("Filter Database")
    st.caption(
        "Upload an Excel filter database or edit rows manually. These values are stored in the project session."
    )

    uploaded_file = st.file_uploader(
        "Upload Excel filter database",
        type=["xlsx", "xlsm", "xls"],
        help="If your workbook has a Filter_Database sheet, select it after upload.",
    )

    if uploaded_file is not None:
        try:
            excel_bytes = uploaded_file.getvalue()
            workbook = pd.ExcelFile(BytesIO(excel_bytes))
            default_sheet = (
                workbook.sheet_names.index("Filter_Database")
                if "Filter_Database" in workbook.sheet_names
                else 0
            )
            selected_sheet = st.selectbox(
                "Select sheet to import",
                workbook.sheet_names,
                index=default_sheet,
                key="filter_database_sheet",
            )
            if st.button("Import selected sheet", use_container_width=True):
                imported = read_excel_database(BytesIO(excel_bytes), selected_sheet)
                st.session_state.filter_database_data = imported
                persist_filter_database_dataframe(imported)
                st.session_state.filter_database_nonce = st.session_state.get(
                    "filter_database_nonce", 0
                ) + 1
                st.success(f"Imported {len(imported)} rows from {selected_sheet}.")
                st.rerun()
        except Exception as exc:
            st.error(f"Cannot read uploaded Excel file: {exc}")

    current_df = st.session_state.get("filter_database_data")
    if current_df is None:
        current_df = records_to_dataframe(records)
        st.session_state.filter_database_data = normalize_display_dataframe(current_df)
    current_df = normalize_display_dataframe(st.session_state.filter_database_data)

    render_quick_add_filter_form(current_df)

    saved_df = normalize_display_dataframe(st.session_state.get("filter_database_data"))
    st.markdown("**Filter Records**")
    st.caption("Use the form above to add or edit filters. This table is for review and selection in Scenarios.")
    st.dataframe(saved_df, use_container_width=True, hide_index=True)
    saved_df = render_filter_record_delete_tools(saved_df)

    col1, col2, col3 = st.columns(3)
    if col1.button("Clear database", use_container_width=True):
        empty_df = pd.DataFrame(columns=list(DISPLAY_COLUMNS.values()))
        st.session_state.filter_database_data = empty_df
        persist_filter_database_dataframe(empty_df)
        st.session_state.filter_database_nonce = st.session_state.get(
            "filter_database_nonce", 0
        ) + 1
        st.rerun()
    col2.download_button(
        "Download database CSV",
        data=saved_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="filter_database.csv",
        mime="text/csv",
        use_container_width=True,
    )
    col3.download_button(
        "Download database Excel",
        data=dataframe_to_excel_bytes(saved_df),
        file_name="filter_database.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    return dataframe_to_records(saved_df)
