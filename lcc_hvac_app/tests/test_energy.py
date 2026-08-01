from lcc_hvac_app.engine.energy import calculate_energy_cost_year, calculate_energy_kwh_year


def test_energy_kwh_year_formula():
    result = calculate_energy_kwh_year(
        airflow_m3_h=3600,
        avg_dp_pa=100,
        operating_hours_day=10,
        operating_days_year=100,
        fan_efficiency=0.5,
        number_of_ahu=2,
    )
    assert result == 400.0


def test_energy_cost_year_formula():
    assert calculate_energy_cost_year(400, 2500) == 1_000_000
