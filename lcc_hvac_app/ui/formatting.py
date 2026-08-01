from __future__ import annotations

import math


def money(value: float, currency: str = "VND") -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{value:,.0f} {currency}"


def number(value: float, decimals: int = 2) -> str:
    if value == float("inf"):
        return "No replacement"
    return f"{value:,.{decimals}f}"
