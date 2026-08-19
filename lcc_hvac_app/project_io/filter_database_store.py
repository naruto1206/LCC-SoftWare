from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from lcc_hvac_app.engine.models import FilterDatabaseRecord

PACKAGE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_FILTER_DATABASE_PATH = PACKAGE_DIR / "data" / "filter_database.csv"

FILTER_DATABASE_FIELDS = [
    "filter_id",
    "supplier",
    "filter_type",
    "stage",
    "model",
    "size",
    "filter_class",
    "qty_per_ahu",
    "dhc_g",
    "initial_dp_pa",
    "avg_dp_pa",
    "final_dp_pa",
    "mass_efficiency",
    "price_vnd_filter",
    "notes",
]

NUMBER_FIELDS = {
    "qty_per_ahu",
    "dhc_g",
    "initial_dp_pa",
    "avg_dp_pa",
    "final_dp_pa",
    "mass_efficiency",
    "price_vnd_filter",
}


def _to_float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return 0.0


def load_filter_database(
    path: str | Path = DEFAULT_FILTER_DATABASE_PATH,
) -> list[FilterDatabaseRecord]:
    input_path = Path(path)
    if not input_path.exists():
        return []

    records: list[FilterDatabaseRecord] = []
    with input_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if not any(str(row.get(field, "")).strip() for field in FILTER_DATABASE_FIELDS):
                continue
            if not str(row.get("qty_per_ahu", "") or "").strip():
                row["qty_per_ahu"] = "1"
            normalized = {
                field: _to_float(row.get(field, 0))
                if field in NUMBER_FIELDS
                else str(row.get(field, "") or "").strip()
                for field in FILTER_DATABASE_FIELDS
            }
            records.append(FilterDatabaseRecord(**normalized))
    return records


def save_filter_database(
    records: list[FilterDatabaseRecord],
    path: str | Path = DEFAULT_FILTER_DATABASE_PATH,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FILTER_DATABASE_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow({field: getattr(record, field) for field in FILTER_DATABASE_FIELDS})
    return output_path
