def calculate_energy_kwh_year(
    airflow_m3_h: float,
    avg_dp_pa: float,
    operating_hours_day: float,
    operating_days_year: float,
    fan_efficiency: float,
    number_of_ahu: float,
) -> float:
    if fan_efficiency <= 0:
        raise ValueError("Fan efficiency must be greater than 0.")
    airflow_m3_s = airflow_m3_h / 3600.0
    operating_hours_year = operating_hours_day * operating_days_year
    return airflow_m3_s * avg_dp_pa * operating_hours_year / (1000.0 * fan_efficiency) * number_of_ahu


def calculate_energy_cost_year(energy_kwh_year: float, electricity_price_vnd_kwh: float) -> float:
    return energy_kwh_year * electricity_price_vnd_kwh
