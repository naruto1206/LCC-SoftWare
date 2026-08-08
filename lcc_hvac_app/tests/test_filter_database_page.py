from io import BytesIO

import pandas as pd
from openpyxl import load_workbook

from lcc_hvac_app.ui.filter_database_page import (
    dataframe_to_excel_bytes,
    filter_record_ids,
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
