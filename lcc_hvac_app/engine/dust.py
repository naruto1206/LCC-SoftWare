def calculate_dust_entering(
    airflow_m3_h: float,
    dust_concentration_mg_m3: float,
    environment_factor: float,
    operating_hours_day: float,
    qty_per_ahu: float,
) -> float:
    if qty_per_ahu <= 0:
        raise ValueError("Qty/AHU must be greater than 0.")
    return (
        airflow_m3_h
        * dust_concentration_mg_m3
        * environment_factor
        * operating_hours_day
        / 1000.0
        / qty_per_ahu
    )


def calculate_dust_captured(dust_entering_day_filter: float, mass_efficiency: float) -> float:
    efficiency = mass_efficiency / 100.0 if mass_efficiency > 1 else mass_efficiency
    return max(dust_entering_day_filter * efficiency, 0.0)


def calculate_dust_to_next_stage(
    dust_entering_day_filter: float, dust_captured_day_filter: float
) -> float:
    return max(dust_entering_day_filter - dust_captured_day_filter, 0.0)
