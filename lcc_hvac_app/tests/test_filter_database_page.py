from io import BytesIO

import pandas as pd
from openpyxl import load_workbook

from lcc_hvac_app.ui.filter_database_page import (
    dataframe_to_excel_bytes,
    filter_record_ids,
    normalize_uploaded_database,
    recalculate_media_area_dataframe,
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
                "ISO Class": "ISO Coarse 60%",
                "DHC/filter direct (g)": 450,
            }
        ]
    )

    workbook = load_workbook(filename=BytesIO(dataframe_to_excel_bytes(dataframe)))

    assert "Filter_Database" in workbook.sheetnames
    assert "_Lists" in workbook.sheetnames
    assert workbook["_Lists"].sheet_state == "hidden"
    worksheet = workbook["Filter_Database"]
    assert worksheet["A1"].value == "Filter ID"
    assert worksheet["A2"].value == "PF-001"
    assert "ISO Class" in [cell.value for cell in worksheet[1]]
    assert worksheet["A1"].fill.fgColor.rgb == "000F766E"
    assert worksheet["A2"].fill.fgColor.rgb == "00DCFCE7"
    assert worksheet.freeze_panes == "A2"
    assert len(worksheet.data_validations.dataValidation) >= 1
    assert worksheet["I2"].value == "=IF(AND(G2>0,H2>0),ROUND(G2*H2/1000000,4),0)"
    assert "ePM1 %" in [cell.value for cell in worksheet[1]]
    assert "Mass Eff. Source" in [cell.value for cell in worksheet[1]]
    assert any(
        validation.formula1.startswith("'_Lists'!$B$2:$B$")
        for validation in worksheet.data_validations.dataValidation
    )


def test_recalculate_media_area_dataframe_uses_width_and_height():
    dataframe = pd.DataFrame(
        [
            {
                "Filter ID": "PF-001",
                "Width (mm)": 592,
                "Height (mm)": 592,
                "Media area/filter (m2)": 0,
            }
        ]
    )

    normalized = recalculate_media_area_dataframe(dataframe)

    assert normalized.loc[0, "Media area/filter (m2)"] == 0.3505


def test_normalize_uploaded_database_imports_qty_per_ahu():
    dataframe = pd.DataFrame(
        [
            {
                "Filter ID": "PF-A",
                "Stage": "Pre-filter",
                "ISO Class": "ISO Coarse 70%",
                "Size": "592x287x46",
                "Qty/AHU": 20,
                "DHC to final DP (g)": 600,
                "Area (m2)": 1.2,
                "Eurovent Avg DP (Pa)": 85,
                "Mass Efficiency %": 70,
                "Price/filter (VND)": 250000,
            }
        ]
    )

    normalized = normalize_uploaded_database(dataframe)

    assert normalized.loc[0, "Filter ID"] == "PF-A"
    assert normalized.loc[0, "ISO Class"] == "ISO Coarse 70%"
    assert normalized.loc[0, "Qty/AHU"] == 20
    assert normalized.loc[0, "Width (mm)"] == 592
    assert normalized.loc[0, "Height (mm)"] == 287
    assert normalized.loc[0, "DHC/filter direct (g)"] == 600
    assert normalized.loc[0, "Media area/filter (m2)"] == 0.1699
    assert normalized.loc[0, "Avg DP (Pa)"] == 85
    assert normalized.loc[0, "Mass Eff. %"] == 70
    assert normalized.loc[0, "Price/filter (VND)"] == 250000


def test_normalize_uploaded_database_estimates_mass_efficiency_from_epm():
    dataframe = pd.DataFrame(
        [
            {
                "Filter ID": "FF-A",
                "Stage": "Fine-filter",
                "ePM10 %": 60,
                "ISO Coarse %": 90,
            }
        ]
    )

    normalized = normalize_uploaded_database(dataframe)

    assert normalized.loc[0, "Mass Eff. %"] == 70.5
    assert normalized.loc[0, "Mass Eff. Source"] == "Estimated from ePM/Coarse"


def test_normalize_uploaded_database_estimates_mass_efficiency_from_iso_class():
    dataframe = pd.DataFrame(
        [
            {
                "Filter ID": "FF-B",
                "Stage": "Fine-filter",
                "ISO Class": "ISO ePM1 50%",
            }
        ]
    )

    normalized = normalize_uploaded_database(dataframe)

    assert normalized.loc[0, "ePM1 %"] == 0
    assert normalized.loc[0, "Mass Eff. %"] == 50
    assert normalized.loc[0, "Mass Eff. Source"] == "Estimated from ePM/Coarse"


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
    assert normalized.loc[0, "DHC/filter direct (g)"] == 600
