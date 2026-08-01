from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ISO_GROUP_MX_G = {
    "ISO ePM1": 200.0,
    "ISO ePM2.5": 250.0,
    "ISO ePM10": 400.0,
    "ISO Coarse": 400.0,
}


@dataclass
class EuroventSegment:
    step: int
    previous_dust_fed_g: float
    dust_fed_g: float
    previous_dp_pa: float
    dp_pa: float
    dust_increment_g: float
    segment_avg_dp_pa: float
    weighted_dp_g_pa: float
    used_to_mx: bool


@dataclass
class EuroventAverageDPResult:
    average_dp_pa: float
    mx_g: float
    covered_dust_g: float
    weighted_dp_sum: float
    segments: list[EuroventSegment]


def estimate_average_dp(initial_dp_pa: float, final_dp_pa: float) -> float:
    if initial_dp_pa < 0 or final_dp_pa < 0:
        raise ValueError("DP values cannot be negative.")
    return (initial_dp_pa + final_dp_pa) / 2.0


def default_mx_for_iso_group(iso_group: str) -> float:
    return ISO_GROUP_MX_G.get(iso_group, 200.0)


def normalize_curve_points(points: list[dict[str, Any]]) -> list[dict[str, float]]:
    normalized: list[dict[str, float]] = []
    for point in points:
        dust = _to_float(point.get("dust_fed_g"))
        dp = _to_float(point.get("pressure_drop_pa"))
        if dust is None or dp is None:
            continue
        if dust < 0 or dp < 0:
            raise ValueError("Dust fed and pressure drop values cannot be negative.")
        normalized.append({"dust_fed_g": dust, "pressure_drop_pa": dp})
    return sorted(normalized, key=lambda row: row["dust_fed_g"])


def calculate_eurovent_average_dp(
    points: list[dict[str, Any]],
    mx_g: float,
) -> EuroventAverageDPResult:
    if mx_g <= 0:
        raise ValueError("Mx must be greater than 0.")

    normalized = normalize_curve_points(points)
    if len(normalized) < 2:
        raise ValueError("At least two dust/DP points are required.")

    segments: list[EuroventSegment] = []
    weighted_sum = 0.0
    covered_dust = 0.0
    for index in range(1, len(normalized)):
        previous = normalized[index - 1]
        current = normalized[index]
        previous_dust = previous["dust_fed_g"]
        current_dust = current["dust_fed_g"]
        dust_increment = max(min(current_dust, mx_g) - min(previous_dust, mx_g), 0.0)
        segment_avg_dp = (previous["pressure_drop_pa"] + current["pressure_drop_pa"]) / 2.0
        weighted = dust_increment * segment_avg_dp if dust_increment > 0 else 0.0
        weighted_sum += weighted
        covered_dust += dust_increment
        segments.append(
            EuroventSegment(
                step=index,
                previous_dust_fed_g=previous_dust,
                dust_fed_g=current_dust,
                previous_dp_pa=previous["pressure_drop_pa"],
                dp_pa=current["pressure_drop_pa"],
                dust_increment_g=dust_increment,
                segment_avg_dp_pa=segment_avg_dp,
                weighted_dp_g_pa=weighted,
                used_to_mx=dust_increment > 0,
            )
        )

    return EuroventAverageDPResult(
        average_dp_pa=weighted_sum / mx_g,
        mx_g=mx_g,
        covered_dust_g=covered_dust,
        weighted_dp_sum=weighted_sum,
        segments=segments,
    )


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None
