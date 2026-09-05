from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OutdoorEnvironmentProfile:
    label: str
    dust_concentration_mg_m3: float
    environment_factor: float
    pm1_fraction: float
    pm1_to_25_fraction: float
    pm25_to_10_fraction: float
    coarse_fraction: float


OUTDOOR_ENVIRONMENT_PROFILES: dict[str, OutdoorEnvironmentProfile] = {
    "Rural area (ODA1)": OutdoorEnvironmentProfile(
        "Rural area (ODA1)", 0.05, 0.80, 0.08, 0.12, 0.30, 0.50
    ),
    "Country town": OutdoorEnvironmentProfile(
        "Country town", 0.10, 1.00, 0.12, 0.18, 0.35, 0.35
    ),
    "Large town (ODA2)": OutdoorEnvironmentProfile(
        "Large town (ODA2)", 0.20, 1.20, 0.18, 0.22, 0.35, 0.25
    ),
    "Industrial town (ODA3)": OutdoorEnvironmentProfile(
        "Industrial town (ODA3)", 0.35, 1.50, 0.15, 0.20, 0.30, 0.35
    ),
    "Industrial area": OutdoorEnvironmentProfile(
        "Industrial area", 0.60, 2.00, 0.12, 0.18, 0.25, 0.45
    ),
}

DEFAULT_OUTDOOR_ENVIRONMENT = "Country town"


def normalize_percent(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    try:
        number = float(str(value).replace(",", "").replace("%", "").strip())
    except ValueError:
        return 0.0
    if number < 0:
        return 0.0
    if number <= 1:
        return number
    return number / 100.0


def percent_for_display(value: Any) -> float:
    return round(normalize_percent(value) * 100.0, 4)


def environment_profile(name: str | None) -> OutdoorEnvironmentProfile:
    if name in OUTDOOR_ENVIRONMENT_PROFILES:
        return OUTDOOR_ENVIRONMENT_PROFILES[str(name)]
    return OUTDOOR_ENVIRONMENT_PROFILES[DEFAULT_OUTDOOR_ENVIRONMENT]


def parse_iso_class_efficiencies(iso_class: Any) -> dict[str, float]:
    text = str(iso_class or "").strip()
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    if match is None:
        return {}
    value = percent_for_display(match.group(1))
    lower_text = text.lower().replace(",", ".")
    if "epm2.5" in lower_text or "epm25" in lower_text:
        return {"epm25_percent": value}
    if "epm10" in lower_text:
        return {"epm10_percent": value}
    if "epm1" in lower_text:
        return {"epm1_percent": value}
    if "coarse" in lower_text:
        return {"coarse_percent": value}
    return {}


def estimate_mass_efficiency(
    epm1_percent: Any = 0.0,
    epm25_percent: Any = 0.0,
    epm10_percent: Any = 0.0,
    coarse_percent: Any = 0.0,
    outdoor_environment: str | None = None,
) -> float:
    profile = environment_profile(outdoor_environment)
    epm1 = normalize_percent(epm1_percent)
    epm25 = normalize_percent(epm25_percent)
    epm10 = normalize_percent(epm10_percent)
    coarse = normalize_percent(coarse_percent)

    if max(epm1, epm25, epm10, coarse) <= 0:
        return 0.0

    pm1_eff = epm1 or epm25 or epm10 or coarse
    pm1_to_25_eff = epm25 or epm10 or coarse or epm1
    pm25_to_10_eff = epm10 or coarse or epm25 or epm1
    coarse_eff = coarse or epm10 or epm25 or epm1

    estimate = (
        profile.pm1_fraction * pm1_eff
        + profile.pm1_to_25_fraction * pm1_to_25_eff
        + profile.pm25_to_10_fraction * pm25_to_10_eff
        + profile.coarse_fraction * coarse_eff
    )
    return round(min(max(estimate, 0.0), 1.0), 4)


def effective_mass_efficiency(
    direct_mass_efficiency: Any = 0.0,
    epm1_percent: Any = 0.0,
    epm25_percent: Any = 0.0,
    epm10_percent: Any = 0.0,
    coarse_percent: Any = 0.0,
    outdoor_environment: str | None = None,
    iso_class: Any = "",
) -> tuple[float, str]:
    direct = normalize_percent(direct_mass_efficiency)
    if direct > 0:
        return round(direct, 4), "Direct"
    parsed_iso = parse_iso_class_efficiencies(iso_class)
    estimated = estimate_mass_efficiency(
        epm1_percent or parsed_iso.get("epm1_percent", 0.0),
        epm25_percent or parsed_iso.get("epm25_percent", 0.0),
        epm10_percent or parsed_iso.get("epm10_percent", 0.0),
        coarse_percent or parsed_iso.get("coarse_percent", 0.0),
        outdoor_environment,
    )
    if estimated > 0:
        return estimated, "Estimated from ePM/Coarse"
    return 0.0, "Missing"
