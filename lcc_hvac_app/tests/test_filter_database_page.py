from io import BytesIO

import pandas as pd
from openpyxl import load_workbook

from lcc_hvac_app.ui.filter_database_page import (
    dataframe_to_excel_bytes,
    filter_record_ids,
    normalize_uploaded_database,
    remove_filter_database_rows,
)


def test_remove_filter_database_rows_removes_selected_ids():
    dataframe = pd.DataFrame(
        [
            {"Filter ID": "PF-001", "Supplier": "Air Filtech"},
            {"Filter ID": "FF-001", "Supplier": "Air Filtech"},
            {"Filter ID": "HEPA-001", "Supplier": "Air Filtech"},
        ]
    )

    remaining = remove_filter_database_rows(dataframe, ["PF-001", "HEPA-001"])

    assert remaining["Filter ID"].tolist() == ["FF-001"]


def test_filter_record_ids_skips_empty_values():
    dataframe = pd.DataFrame(
        [
            {"Filter ID": "PF-001"},
            {"Filter ID": ""},
            {"Filter ID": None},
            {"Filter ID": "FF-001"},
        ]
    )

    assert filter_record_ids(dataframe) == ["PF-001", "FF-001"]


def test_dataframe_to_excel_bytes_exports_filter_database_sheet():
    dataframe = pd.DataFrame(
        [
            {
                "Filter ID": "PF-001",
                "Supplier": "Air Filtech",
                "Stage": "Pre-filter",
                "DHC (g)": 450,
            }
        ]
    )

    workbook = load_workbook(filename=BytesIO(dataframe_to_excel_bytes(dataframe)))

    assert "Filter_Database" in workbook.sheetnames
    worksheet = workbook["Filter_Database"]
    assert worksheet["A1"].value == "Filter ID"
    assert worksheet["A2"].value == "PF-001"


def test_normalize_uploaded_database_imports_qty_per_ahu():
    dataframe = pd.DataFrame(
        [
            {
                "Filter ID": "PF-A",
                "Stage": "Pre-filter",
                "ISO Class": "ISO Coarse 70%",
                "Qty/AHU": 20,
                "DHC to final DP (g)": 600,
                "Eurovent Avg DP (Pa)": 85,
                "Mass Efficiency %": 0.7,
                "Price/filter (VND)": 250000,
            }
        ]
    )

    normalized = normalize_uploaded_database(dataframe)

    assert normalized.loc[0, "Filter ID"] == "PF-A"
    assert normalized.loc[0, "Qty/AHU"] == 20
    assert normalized.loc[0, "DHC (g)"] == 600
    assert normalized.loc[0, "Avg DP (Pa)"] == 85
    assert normalized.loc[0, "Mass Efficiency"] == 0.7
    assert normalized.loc[0, "Price/filter"] == 250000


def test_normalize_uploaded_database_detects_workbook_header_row():
    dataframe = pd.DataFrame(
        [
            ["FILTER DATABASE", None, None, None],
            ["Description", None, None, None],
            ["Filter ID", "Stage", "Qty/AHU", "DHC to final DP (g)"],
            ["PF-A", "Pre-filter", 20, 600],
        ]
    )

    normalized = normalize_uploaded_database(dataframe)

    assert normalized.loc[0, "Filter ID"] == "PF-A"
    assert normalized.loc[0, "Stage"] == "Pre-filter"
    assert normalized.loc[0, "Qty/AHU"] == 20
    assert normalized.loc[0, "DHC (g)"] == 600
