from lcc_hvac_app.engine.models import default_project
from lcc_hvac_app.project_io.json_store import load_project_from_bytes, project_to_payload


def test_project_json_round_trip_from_bytes():
    project = default_project()
    project.project_info.customer = "Customer Test"
    project.project_info.location = "Location Test"
    payload = project_to_payload(project)
    import json

    loaded = load_project_from_bytes(json.dumps(payload).encode("utf-8"))

    assert loaded.project_info.project_name == project.project_info.project_name
    assert loaded.project_info.customer == "Customer Test"
    assert loaded.project_info.location == "Location Test"
    assert len(loaded.scenarios) == 4
    assert loaded.scenarios[0].stages[0].stage == "Pre-filter"
