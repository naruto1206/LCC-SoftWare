from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ProjectInfo:
    project_name: str = "AHU Filter LCC 2026"
    customer: str = "Factory A"
    location: str = "Binh Duong"
    engineer: str = "Air Filtech/LCC"
    date: str = "2026-07-07"
    currency: str = "VND"


@dataclass
class Assumptions:
    airflow_m3_h_per_ahu: float = 20000.0
    number_of_ahu: int = 1
    operating_hours_day: float = 24.0
    operating_days_year: float = 365.0
    fan_efficiency: float = 0.6
    electricity_price_vnd_kwh: float = 2500.0
    dust_concentration_mg_m3: float = 0.3
    environment_factor: float = 1.0
    labor_cost_vnd_filter_change: float = 50000.0
    disposal_cost_vnd_filter_change: float = 20000.0
    downtime_cost_vnd_change: float = 0.0
    co2_emission_factor_kg_kwh: float = 0.85
    analysis_period_years: int = 5


@dataclass
class FilterStage:
    stage: str = "Pre-filter"
    qty_per_ahu: float = 1.0
    dhc_g: float = 500.0
    mass_efficiency: float = 0.5
    avg_dp_pa: float = 80.0
    price_vnd_filter: float = 100000.0
    width_mm: float = 0.0
    height_mm: float = 0.0
    media_area_m2: float = 0.0
    filter_id: str = ""
    eurovent_iso_group: str = "ISO ePM1"
    eurovent_mx_g: float = 200.0
    eurovent_curve: list[dict[str, float]] = field(default_factory=list)

    def normalized_efficiency(self) -> float:
        if self.mass_efficiency > 1:
            return self.mass_efficiency / 100.0
        return self.mass_efficiency


@dataclass
class FilterDatabaseRecord:
    filter_id: str = ""
    supplier: str = ""
    filter_type: str = ""
    stage: str = ""
    model: str = ""
    size: str = ""
    filter_class: str = ""
    qty_per_ahu: float = 1.0
    width_mm: float = 0.0
    height_mm: float = 0.0
    media_area_m2: float = 0.0
    dhc_g: float = 0.0
    initial_dp_pa: float = 0.0
    avg_dp_pa: float = 0.0
    final_dp_pa: float = 0.0
    mass_efficiency: float = 0.0
    price_vnd_filter: float = 0.0
    notes: str = ""


@dataclass
class Scenario:
    name: str
    stages: list[FilterStage] = field(default_factory=list)


@dataclass
class Project:
    project_info: ProjectInfo = field(default_factory=ProjectInfo)
    assumptions: Assumptions = field(default_factory=Assumptions)
    filter_database: list[FilterDatabaseRecord] = field(default_factory=list)
    scenarios: list[Scenario] = field(default_factory=list)
    calculation_results: dict[str, Any] = field(default_factory=dict)
    formula_version: str = "1.0.0"


def dataclass_to_dict(value: Any) -> dict[str, Any]:
    return asdict(value)


def default_stages() -> list[FilterStage]:
    return [
        FilterStage("Pre-filter", 8, 450, 0.55, 75, 110000),
        FilterStage("Fine-filter", 8, 650, 0.85, 120, 260000),
        FilterStage("HEPA", 4, 900, 0.99, 220, 950000),
    ]


def default_filter_database() -> list[FilterDatabaseRecord]:
    return [
        FilterDatabaseRecord(
            filter_id="PF-001",
            supplier="Air Filtech",
            stage="Pre-filter",
            model="Pre-filter sample",
            size="592x592x46",
            filter_class="G4 / ISO Coarse",
            qty_per_ahu=8,
            dhc_g=450,
            initial_dp_pa=45,
            avg_dp_pa=75,
            final_dp_pa=150,
            mass_efficiency=0.55,
            price_vnd_filter=110000,
        ),
        FilterDatabaseRecord(
            filter_id="FF-001",
            supplier="Air Filtech",
            stage="Fine-filter",
            model="Fine-filter sample",
            size="592x592x600",
            filter_class="F8 / ePM1",
            qty_per_ahu=8,
            dhc_g=650,
            initial_dp_pa=80,
            avg_dp_pa=120,
            final_dp_pa=250,
            mass_efficiency=0.85,
            price_vnd_filter=260000,
        ),
        FilterDatabaseRecord(
            filter_id="HEPA-001",
            supplier="Air Filtech",
            stage="HEPA",
            model="HEPA sample",
            size="610x610x292",
            filter_class="H13",
            qty_per_ahu=4,
            dhc_g=900,
            initial_dp_pa=140,
            avg_dp_pa=220,
            final_dp_pa=450,
            mass_efficiency=0.99,
            price_vnd_filter=950000,
        ),
    ]


def default_project() -> Project:
    return Project(
        filter_database=default_filter_database(),
        scenarios=[
            Scenario("Base / Current", default_stages()),
            Scenario(
                "Option 1",
                [
                    FilterStage("Pre-filter", 8, 700, 0.6, 60, 150000),
                    FilterStage("Fine-filter", 8, 900, 0.9, 95, 330000),
                    FilterStage("HEPA", 4, 1000, 0.99, 180, 1050000),
                ],
            ),
            Scenario(
                "Option 2",
                [
                    FilterStage("Pre-filter", 8, 600, 0.55, 65, 135000),
                    FilterStage("Fine-filter", 8, 1100, 0.88, 90, 390000),
                    FilterStage("HEPA", 4, 1100, 0.995, 175, 1150000),
                ],
            ),
            Scenario(
                "Option 3",
                [
                    FilterStage("Pre-filter", 8, 650, 0.6, 70, 145000),
                    FilterStage("Fine-filter", 8, 950, 0.9, 100, 350000),
                    FilterStage("HEPA", 4, 1200, 0.995, 170, 1250000),
                ],
            ),
        ]
    )


def project_from_dict(data: dict[str, Any]) -> Project:
    info = ProjectInfo(**data.get("project_info", {}))
    assumptions = Assumptions(**data.get("assumptions", {}))
    filter_database = [
        FilterDatabaseRecord(**record)
        for record in data.get("filter_database", data.get("filter_database_records", []))
    ]
    scenarios = []
    for scenario_data in data.get("scenarios", []):
        stages = [FilterStage(**stage) for stage in scenario_data.get("stages", [])]
        scenarios.append(Scenario(scenario_data.get("name", "Scenario"), stages))
    return Project(
        project_info=info,
        assumptions=assumptions,
        filter_database=filter_database,
        scenarios=scenarios,
        calculation_results=data.get("calculation_results", {}),
        formula_version=data.get("formula_version", "1.0.0"),
    )
