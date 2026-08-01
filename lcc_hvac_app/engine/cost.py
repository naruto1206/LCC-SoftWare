def calculate_filter_cost_year(
    replacement_year: float,
    price_vnd_filter: float,
    qty_per_ahu: float,
    number_of_ahu: float,
) -> float:
    return replacement_year * price_vnd_filter * qty_per_ahu * number_of_ahu


def calculate_labor_disposal_cost_year(
    replacement_year: float,
    qty_per_ahu: float,
    labor_cost_vnd_filter_change: float,
    disposal_cost_vnd_filter_change: float,
    downtime_cost_vnd_change: float,
    number_of_ahu: float,
) -> float:
    labor_disposal = (
        replacement_year
        * qty_per_ahu
        * (labor_cost_vnd_filter_change + disposal_cost_vnd_filter_change)
        * number_of_ahu
    )
    downtime = replacement_year * downtime_cost_vnd_change * number_of_ahu
    return labor_disposal + downtime
