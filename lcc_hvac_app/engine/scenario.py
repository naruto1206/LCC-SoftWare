from __future__ import annotations

from .models import Assumptions, Scenario
from .tco import calculate_scenario_tco


def compare_scenarios(
    scenarios: list[Scenario], assumptions: Assumptions
) -> dict[str, object]:
    calculated = [calculate_scenario_tco(scenario, assumptions) for scenario in scenarios]
    if not calculated:
        return {"summaries": [], "stages": [], "best_option": None}

    base_tco = float(calculated[0]["summary"]["tco_year"])
    summaries = []
    stages = []
    for scenario_result in calculated:
        summary = dict(scenario_result["summary"])
        tco = float(summary["tco_year"])
        saving = base_tco - tco
        summary["saving_vs_base"] = saving
        summary["saving_percent"] = (saving / base_tco * 100.0) if base_tco else 0.0
        summaries.append(summary)
        for stage in scenario_result["stages"]:
            stage_row = dict(stage)
            stage_row["scenario"] = summary["scenario"]
            stages.append(stage_row)

    best = min(summaries, key=lambda row: float(row["tco_year"]))
    return {"summaries": summaries, "stages": stages, "best_option": best["scenario"]}
