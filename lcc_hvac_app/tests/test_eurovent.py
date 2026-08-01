from lcc_hvac_app.engine.eurovent import calculate_eurovent_average_dp


def test_eurovent_average_dp_matches_excel_sample() -> None:
    points = [
        {"dust_fed_g": 0, "pressure_drop_pa": 68},
        {"dust_fed_g": 30, "pressure_drop_pa": 69},
        {"dust_fed_g": 70, "pressure_drop_pa": 70},
        {"dust_fed_g": 100, "pressure_drop_pa": 71},
        {"dust_fed_g": 150, "pressure_drop_pa": 74},
        {"dust_fed_g": 180, "pressure_drop_pa": 76},
        {"dust_fed_g": 200, "pressure_drop_pa": 78},
        {"dust_fed_g": 230, "pressure_drop_pa": 80},
        {"dust_fed_g": 260, "pressure_drop_pa": 85},
    ]

    result = calculate_eurovent_average_dp(points, 200)

    assert result.average_dp_pa == 71.825
    assert result.covered_dust_g == 200
    assert result.segments[-1].dust_increment_g == 0
