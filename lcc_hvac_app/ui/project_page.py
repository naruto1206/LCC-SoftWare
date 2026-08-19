from __future__ import annotations

import streamlit as st

from lcc_hvac_app.engine.models import ProjectInfo


def _project_text_input(label: str, value: str, key: str) -> str:
    if key not in st.session_state:
        st.session_state[key] = value
    return st.text_input(label, key=key)


def render_project_info(info: ProjectInfo) -> ProjectInfo:
    st.markdown("**Report Identity**")
    left, right = st.columns(2)
    with left:
        project_name = _project_text_input(
            "Project name",
            info.project_name,
            "project_info_project_name",
        )
        customer = _project_text_input("Customer", info.customer, "project_info_customer")
        location = _project_text_input("Location", info.location, "project_info_location")
    with right:
        engineer = _project_text_input("Engineer", info.engineer, "project_info_engineer")
        date = _project_text_input("Date", info.date, "project_info_date")
        currency = _project_text_input("Currency", info.currency, "project_info_currency")
    st.info("These fields appear in the project context bar and exported Excel report.")
    return ProjectInfo(
        project_name=project_name,
        customer=customer,
        location=location,
        engineer=engineer,
        date=date,
        currency=currency,
    )
