def calculate_filter_life_days(dhc_g: float, dust_captured_day_filter: float) -> float:
    if dhc_g <= 0:
        raise ValueError("DHC must be greater than 0.")
    if dust_captured_day_filter <= 0:
        return float("inf")
    return dhc_g / dust_captured_day_filter


def calculate_replacement_per_year(operating_days_year: float, filter_life_days: float) -> float:
    if filter_life_days == float("inf"):
        return 0.0
    if filter_life_days <= 0:
        raise ValueError("Filter life days must be greater than 0.")
    return operating_days_year / filter_life_days
