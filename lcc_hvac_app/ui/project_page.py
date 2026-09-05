from __future__ import annotations

import streamlit as st

from lcc_hvac_app.engine.models import ProjectInfo


PROJECT_INFO_FIELD_KEYS = {
    "project_name": "project_info_project_name",
    "customer": "project_info_customer",
    "location": "project_info_location",
    "engineer": "project_info_engineer",
    "date": "project_info_date",
    "currency": "project_info_currency",
}


PROJECT_INFO_REQUIRED_LABELS = {
    "project_name": "Project name",
    "customer": "Customer",
    "location": "Location",
    "engineer": "Engineer",
    "date": "Date",
    "currency": "Currency",
}


def project_info_from_session(info: ProjectInfo) -> ProjectInfo:
    values = {}
    for field_name, key in PROJECT_INFO_FIELD_KEYS.items():
        values[field_name] = str(st.session_state.get(key, getattr(info, field_name, ""))).strip()
    return ProjectInfo(**values)


def sync_project_info_from_session(info: ProjectInfo) -> ProjectInfo:
    for field_name, key in PROJECT_INFO_FIELD_KEYS.items():
        if key in st.session_state:
            setattr(info, field_name, st.session_state.get(key, ""))
    return info


def _sync_project_info_field(field_name: str, key: str) -> None:
    project = st.session_state.get("project")
    if project is None or not hasattr(project, "project_info"):
        return
    setattr(project.project_info, field_name, st.session_state.get(key, ""))


def _project_text_input(label: str, value: str, key: str, field_name: str) -> str:
    if key not in st.session_state:
        st.session_state[key] = value
    return st.text_input(
        label,
        key=key,
        on_change=_sync_project_info_field,
        args=(field_name, key),
    )


def _missing_project_info_fields(info: ProjectInfo) -> list[str]:
    return [
        label
        for field_name, label in PROJECT_INFO_REQUIRED_LABELS.items()
        if not str(getattr(info, field_name, "")).strip()
    ]


def _commit_project_info(info: ProjectInfo) -> None:
    project = st.session_state.get("project")
    if project is not None and hasattr(project, "project_info"):
        project.project_info = info
        st.session_state.project = project
    st.session_state.flash_message = "Project created and information synced with the system."
    st.rerun()


def render_project_info(info: ProjectInfo) -> ProjectInfo:
    st.markdown("**Report Identity**")
    left, right = st.columns(2)
    with left:
        project_name = _project_text_input(
            "Project name",
            info.project_name,
            "project_info_project_name",
            "project_name",
        )
        customer = _project_text_input(
            "Customer",
            info.customer,
            "project_info_customer",
            "customer",
        )
        location = _project_text_input(
            "Location",
            info.location,
            "project_info_location",
            "location",
        )
    with right:
        engineer = _project_text_input(
            "Engineer",
            info.engineer,
            "project_info_engineer",
            "engineer",
        )
        date = _project_text_input("Date", info.date, "project_info_date", "date")
        currency = _project_text_input(
            "Currency",
            info.currency,
            "project_info_currency",
            "currency",
        )
    entered_info = ProjectInfo(
        project_name=project_name,
        customer=customer,
        location=location,
        engineer=engineer,
        date=date,
        currency=currency,
    )
    missing_fields = _missing_project_info_fields(entered_info)
    if missing_fields:
        st.info("Complete these fields before creating the project: " + ", ".join(missing_fields))

    if st.button(
        "Create Project and Sync Information",
        type="primary",
        width="stretch",
        disabled=bool(missing_fields),
    ):
        _commit_project_info(project_info_from_session(entered_info))

    st.info("These fields appear in the project context bar and exported Excel report.")
    return entered_info
