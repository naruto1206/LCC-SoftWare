from lcc_hvac_app.engine.efficiency import (
    effective_mass_efficiency,
    estimate_mass_efficiency,
    normalize_percent,
    parse_iso_class_efficiencies,
)


def test_normalize_percent_accepts_fraction_and_percent():
    assert normalize_percent(0.7) == 0.7
    assert normalize_percent(70) == 0.7
    assert normalize_percent("70%") == 0.7


def test_effective_mass_efficiency_prefers_direct_value():
    efficiency, source = effective_mass_efficiency(
        direct_mass_efficiency=75,
        epm1_percent=60,
        epm10_percent=80,
        coarse_percent=90,
        outdoor_environment="Industrial area",
    )

    assert efficiency == 0.75
    assert source == "Direct"


def test_estimate_mass_efficiency_uses_outdoor_environment_profile():
    country = estimate_mass_efficiency(
        epm1_percent=0,
        epm25_percent=0,
        epm10_percent=60,
        coarse_percent=90,
        outdoor_environment="Country town",
    )
    industrial = estimate_mass_efficiency(
        epm1_percent=0,
        epm25_percent=0,
        epm10_percent=60,
        coarse_percent=90,
        outdoor_environment="Industrial area",
    )

    assert country == 0.705
    assert industrial == 0.735


def test_parse_iso_class_distinguishes_epm10_from_epm1():
    assert parse_iso_class_efficiencies("ISO ePM10 60%") == {"epm10_percent": 60.0}
    assert parse_iso_class_efficiencies("ISO ePM1 50%") == {"epm1_percent": 50.0}


def test_effective_mass_efficiency_uses_iso_class_when_epm_fields_are_empty():
    efficiency, source = effective_mass_efficiency(
        direct_mass_efficiency=0,
        outdoor_environment="Country town",
        iso_class="ISO ePM1 50%",
    )

    assert efficiency == 0.5
    assert source == "Estimated from ePM/Coarse"
