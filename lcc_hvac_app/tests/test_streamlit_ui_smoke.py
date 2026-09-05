from streamlit.testing.v1 import AppTest


def test_scenario_editor_uses_database_filter_selection_only():
    app_test = AppTest.from_string(
        """
from lcc_hvac_app.engine.models import FilterDatabaseRecord, FilterStage, Scenario
from lcc_hvac_app.ui.scenario_input_page import render_scenario_editor

scenario = Scenario(
    "Option 1",
    [
        FilterStage(
            "Pre-filter",
            qty_per_ahu=20,
            dhc_g=600,
            mass_efficiency=0.7,
            avg_dp_pa=85,
            price_vnd_filter=250000,
            width_mm=592,
            height_mm=592,
            media_area_m2=0.3505,
        ),
        FilterStage(
            "Fine-filter",
            qty_per_ahu=20,
            dhc_g=350,
            mass_efficiency=0.75,
            avg_dp_pa=110,
            price_vnd_filter=1500000,
            width_mm=592,
            height_mm=592,
            media_area_m2=0.3505,
        ),
    ],
)
filter_database = [
    FilterDatabaseRecord(
        filter_id="PF-A",
        stage="Pre-filter",
        model="Coarse Panel",
        qty_per_ahu=20,
        width_mm=592,
        height_mm=592,
        media_area_m2=0.3505,
        dhc_g=600,
        avg_dp_pa=85,
        mass_efficiency=0.7,
        price_vnd_filter=250000,
    )
]
render_scenario_editor(
    scenario,
    key_prefix="smoke_option_1",
    filter_database=filter_database,
)
"""
        )
    app_test.run(timeout=10)

    assert not app_test.exception
    assert len(app_test.number_input) == 0
    assert all(
        option != "Manual input"
        for selectbox in app_test.selectbox
        for option in selectbox.options
    )
