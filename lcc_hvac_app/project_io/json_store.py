from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from lcc_hvac_app import APP_VERSION
from lcc_hvac_app.engine.models import Project, dataclass_to_dict, project_from_dict


def project_to_payload(project: Project) -> dict[str, Any]:
    payload = dataclass_to_dict(project)
    payload["app_version"] = APP_VERSION
    payload["saved_at"] = datetime.now().isoformat(timespec="seconds")
    return payload


def save_project(project: Project, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(project_to_payload(project), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return output_path


def load_project(path: str | Path) -> Project:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return project_from_dict(payload)


def load_project_from_bytes(data: bytes) -> Project:
    payload = json.loads(data.decode("utf-8"))
    return project_from_dict(payload)
