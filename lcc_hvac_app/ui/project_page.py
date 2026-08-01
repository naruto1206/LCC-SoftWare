from __future__ import annotations

import streamlit as st

from lcc_hvac_app.engine.models import ProjectInfo


def render_project_info(info: ProjectInfo) -> ProjectInfo:
    st.markdown("**Report Identity**")
    left, right = st.columns(2)
    with left:
        project_name = st.text_input("Project name", info.project_name)
        customer = st.text_input("Customer", info.customer)
        location = st.text_input("Location", info.location)
    with right:
        engineer = st.text_input("Engineer", info.engineer)
        date = st.text_input("Date", info.date)
        currency = st.text_input("Currency", info.currency)
    st.info("These fields appear in the project context bar and exported Excel report.")
    return ProjectInfo(project_name, customer, location, engineer, date, currency)
