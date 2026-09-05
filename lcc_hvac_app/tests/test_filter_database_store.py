from lcc_hvac_app.engine.models import FilterDatabaseRecord
from lcc_hvac_app.project_io.filter_database_store import (
    load_filter_database,
    save_filter_database,
)


def test_filter_database_csv_round_trip(tmp_path):
    output_path = tmp_path / "filter_database.csv"
    records = [
        FilterDatabaseRecord(
            filter_id="TEST-001",
            supplier="Air Filtech",
            stage="Fine-filter",
            model="Test model",
            filter_class="ISO ePM1 80%",
            qty_per_ahu=20,
            rated_airflow_m3_h_filter=1000,
            width_mm=592,
            height_mm=592,
            media_area_m2=12.5,
            dhc_g=600,
            initial_dp_pa=70,
            avg_dp_pa=115,
            final_dp_pa=250,
            mass_efficiency=0.88,
            price_vnd_filter=320000,
            notes="Saved from app",
        )
    ]

    save_filter_database(records, output_path)
    loaded = load_filter_database(output_path)

    assert len(loaded) == 1
    assert loaded[0].filter_id == "TEST-001"
    assert loaded[0].stage == "Fine-filter"
    assert loaded[0].filter_class == "ISO ePM1 80%"
    assert loaded[0].qty_per_ahu == 20
    assert loaded[0].rated_airflow_m3_h_filter == 1000
    assert loaded[0].width_mm == 592
    assert loaded[0].height_mm == 592
    assert loaded[0].media_area_m2 == 12.5
    assert loaded[0].dhc_g == 600
    assert loaded[0].avg_dp_pa == 115
    assert loaded[0].price_vnd_filter == 320000
