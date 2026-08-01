def calculate_co2_year(energy_kwh_year: float, co2_emission_factor_kg_kwh: float) -> float:
    return energy_kwh_year * co2_emission_factor_kg_kwh
