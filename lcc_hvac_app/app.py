from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

PACKAGE_PARENT = Path(__file__).resolve().parent.parent
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

import streamlit as st

from lcc_hvac_app.engine.models import (
    FilterDatabaseRecord,
    FilterStage,
    Project,
    Scenario,
    default_project,
)
from lcc_hvac_app.engine.efficiency import (
    DEFAULT_OUTDOOR_ENVIRONMENT,
    effective_mass_efficiency,
    environment_profile,
)
from lcc_hvac_app.engine.scenario import compare_scenarios
from lcc_hvac_app.engine.validation import validate_project
from lcc_hvac_app.export.export_excel import build_excel_report
from lcc_hvac_app.project_io.filter_database_store import (
    DEFAULT_FILTER_DATABASE_PATH,
    load_filter_database,
)
from lcc_hvac_app.project_io.json_store import load_project_from_bytes, project_to_payload
from lcc_hvac_app.ui.assumptions_page import render_assumptions
from lcc_hvac_app.ui.dashboard_page import render_dashboard
from lcc_hvac_app.ui.filter_database_page import render_filter_database
from lcc_hvac_app.ui.project_page import render_project_info, sync_project_info_from_session
from lcc_hvac_app.ui.results_page import render_results
from lcc_hvac_app.ui.scenario_input_page import copy_scenario, render_scenario_editor
from lcc_hvac_app.ui.tco_model_page import render_tco_model

PACKAGE_DIR = Path(__file__).resolve().parent
LOGO_PATH = PACKAGE_PARENT / "Logo AIR FILTECH_FA-01.jpg"
if not LOGO_PATH.exists():
    LOGO_PATH = PACKAGE_DIR / "Logo AIR FILTECH_FA-01.jpg"
MENU_PAGES = [
    ("setup", "1. Project Setup"),
    ("filter_data", "2. Filter Data"),
    ("scenarios", "3. Scenarios"),
    ("analysis", "4. Analysis"),
    ("export", "5. Export"),
]
MENU_KEYS = [key for key, _label in MENU_PAGES]
MENU_LABELS = dict(MENU_PAGES)
LEGACY_PAGE_KEYS = {
    "Project": "setup",
    "Assumptions": "setup",
    "Filter Database": "filter_data",
    "Base Current": "scenarios",
    "Option 1": "scenarios",
    "Option 2": "scenarios",
    "Option 3": "scenarios",
    "TCO Model": "analysis",
    "Results": "analysis",
    "Dashboard": "analysis",
    "Export": "export",
    "project": "setup",
    "assumptions": "setup",
    "filter_database": "filter_data",
    "base_current": "scenarios",
    "option_1": "scenarios",
    "option_2": "scenarios",
    "option_3": "scenarios",
    "tco_model": "analysis",
    "results": "analysis",
    "dashboard": "analysis",
}
PAGE_TITLES = {
    "setup": ("Project Setup", "Enter project identity and operating assumptions in one place."),
    "filter_data": ("Filter Data", "Upload or maintain filter records with stage and ISO class choices."),
    "scenarios": ("Scenarios", "Build the current case and proposed options side by side."),
    "analysis": ("Analysis", "Review dashboard, TCO model, formulas, and detailed calculation results."),
    "export": ("Export", "Save the project and download a customer-ready Excel report."),
}


def setup_page() -> None:
    st.set_page_config(
        page_title="LCC Filter System",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        :root {
            --af-primary: #0f766e;
            --af-primary-dark: #123c34;
            --af-primary-soft: #e4f2ee;
            --af-sidebar: #183a31;
            --af-sidebar-soft: #22483e;
            --af-sidebar-text: #d7e4dc;
            --af-text: #263026;
            --af-muted: #7c7464;
            --af-border: #e1d8c6;
            --af-surface: #fffaf0;
            --af-soft: #f6efdf;
            --af-app-bg: #f3ecdc;
            --af-accent: #d99a2b;
            --af-accent-soft: #f4e5c5;
            --af-success: #0f9f8f;
            --af-warning: #b45309;
        }
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(217, 154, 43, 0.12), transparent 30rem),
                var(--af-app-bg);
        }
        .block-container {
            padding-top: 1.05rem;
            padding-bottom: 2.25rem;
            max-width: 1480px;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 0.8rem;
            padding-left: 1.05rem;
            padding-right: 1.05rem;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #17372f 0%, #123029 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 8px 0 24px rgba(18, 48, 41, 0.12);
        }
        section[data-testid="stSidebar"] img {
            display: block;
            margin: 0 auto 0.55rem auto;
            max-width: 78%;
            border-radius: 8px;
        }
        .sidebar-title {
            color: #fff7e8;
            font-size: 1.72rem;
            font-weight: 800;
            line-height: 1.18;
            margin: 0.35rem 0 0.3rem 0;
            text-align: center;
        }
        .sidebar-subtitle {
            color: #b7c9c0;
            font-size: 0.86rem;
            margin: 0 0 0.95rem 0;
            text-align: center;
        }
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] [role="radiogroup"] label,
        section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            font-size: 1rem;
            color: var(--af-sidebar-text);
        }
        section[data-testid="stSidebar"] [data-testid="stRadio"] p {
            font-size: 1rem;
            line-height: 1.45;
            color: var(--af-sidebar-text);
            font-weight: 650;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label {
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 0.45rem 0.48rem;
            margin: 0.1rem 0;
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(255, 250, 240, 0.08);
            border-color: rgba(255, 250, 240, 0.14);
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: #31462c;
            border-color: rgba(217, 154, 43, 0.45);
            box-shadow: inset 4px 0 0 var(--af-accent);
        }
        section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
            color: #ffdb8c;
        }
        section[data-testid="stSidebar"] .stButton button {
            font-size: 1rem;
            min-height: 2.6rem;
            border-color: rgba(255, 250, 240, 0.2);
            background: rgba(255, 250, 240, 0.08);
            color: #fff7e8;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            border-color: var(--af-accent);
            background: rgba(217, 154, 43, 0.18);
            color: #fff7e8;
        }
        .sidebar-project {
            border: 1px solid rgba(255, 250, 240, 0.13);
            border-radius: 8px;
            background: rgba(255, 250, 240, 0.08);
            box-shadow: none;
            padding: 0.7rem 0.78rem;
            margin: 0.55rem 0 0.85rem 0;
            color: #fff7e8;
            font-size: 0.86rem;
        }
        .sidebar-project small {
            color: #b7c9c0;
        }
        .dashboard-brand {
            display: flex;
            align-items: center;
            gap: 1rem; 
            margin: 0.25rem 0 1rem 0;
        }
        .project-context {
            border: 1px solid var(--af-border);
            border-radius: 8px;
            background: rgba(255, 250, 240, 0.92);
            box-shadow: 0 10px 30px rgba(56, 46, 28, 0.06);
            padding: 0.8rem 0.95rem;
            margin: 0 0 1.15rem 0;
        }
        .project-context strong {
            color: var(--af-text);
        }
        .page-label {
            color: var(--af-muted);
            font-size: 0.9rem;
            margin-top: 0.15rem;
        }
        .page-heading {
            margin: 0.1rem 0 0.65rem 0;
            border-bottom: 1px solid var(--af-border);
            padding-bottom: 0.75rem;
        }
        .page-heading h1 {
            color: var(--af-text);
            font-size: 2rem;
            line-height: 1.2;
            margin: 0;
            letter-spacing: 0;
        }
        .page-heading p {
            color: var(--af-muted);
            font-size: 0.98rem;
            margin: 0.25rem 0 0 0;
        }
        .formula-note {
            min-height: 4.25rem;
            border: 1px solid #d8caa8;
            border-radius: 8px;
            background: #fff6df;
            color: #5b4a2a;
            padding: 0.62rem 0.72rem;
            margin: 0 0 0.45rem 0;
            font-size: 0.82rem;
            line-height: 1.35;
        }
        .formula-note strong {
            color: #9a6a0a;
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stDateInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border-color: var(--af-border);
            border-radius: 6px;
            background-color: #fffdf7;
            color: var(--af-text);
        }
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
            color: var(--af-text) !important;
            -webkit-text-fill-color: var(--af-text) !important;
        }
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus {
            border-color: var(--af-accent);
            box-shadow: 0 0 0 1px var(--af-accent);
        }
        div[data-testid="stMetric"] {
            border: 1px solid var(--af-border);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            background: #fffaf0;
            box-shadow: 0 10px 26px rgba(56, 46, 28, 0.06);
            border-top: 3px solid var(--af-accent);
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] [data-testid="stMetricValue"],
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            color: var(--af-text) !important;
        }
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--af-border);
        }
        div[data-testid="stTabs"] [role="tablist"] {
            gap: 0.35rem;
            border-bottom: 1px solid var(--af-border);
        }
        div[data-testid="stTabs"] [role="tab"] {
            background: #efe4ce;
            border: 1px solid #dfd2bb;
            border-bottom: 0;
            border-radius: 8px 8px 0 0;
            padding: 0.55rem 0.9rem;
            color: #6d614d;
            font-weight: 650;
        }
        div[data-testid="stTabs"] [aria-selected="true"] {
            background: #fffaf0;
            color: var(--af-primary-dark);
            border-color: var(--af-border);
            box-shadow: inset 0 3px 0 var(--af-accent);
        }
        div[data-testid="stExpander"] {
            border: 1px solid var(--af-border);
            border-radius: 8px;
            background: #fffaf0;
            box-shadow: 0 8px 22px rgba(56, 46, 28, 0.04);
        }
        .section-label {
            color: var(--af-primary-dark);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin: 0.6rem 0 0.25rem 0;
        }
        .section-title {
            color: var(--af-text);
            font-size: 1.14rem;
            font-weight: 750;
            margin: 0 0 0.45rem 0;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.65rem;
            align-items: stretch;
        }
        .status-item {
            min-height: 4.45rem;
            min-width: 0;
            border: 1px solid #e5d9bf;
            border-left: 3px solid var(--af-accent);
            border-radius: 8px;
            background: #fffdf7;
            padding: 0.62rem 0.72rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .status-label {
            color: var(--af-muted);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .status-value {
            color: var(--af-text);
            font-size: 0.94rem;
            font-weight: 700;
            margin-top: 0.08rem;
            min-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        @media (max-width: 900px) {
            .status-grid {
                grid-template-columns: 1fr 1fr;
            }
            .status-item {
                min-height: 4.25rem;
            }
        }
        @media (max-width: 560px) {
            .status-grid {
                grid-template-columns: 1fr;
            }
        }
        .stButton > button,
        .stDownloadButton > button {
            border-radius: 6px;
            font-weight: 600;
            border-color: #cdbf9f;
            background: #fffaf0;
            color: var(--af-text);
        }
        .stButton > button[kind="primary"] {
            background: var(--af-primary-dark);
            border-color: var(--af-primary-dark);
            color: #fffaf0;
        }
        .stButton > button[kind="primary"]:hover {
            background: #0d4a40;
            border-color: #0d4a40;
        }
        .stDownloadButton > button:hover,
        .stButton > button:hover {
            border-color: var(--af-accent);
            color: var(--af-text);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_project() -> Project:
    if "project" not in st.session_state:
        st.session_state.project = create_new_project()
    ensure_project_schema(st.session_state.project)
    return st.session_state.project


def ensure_project_schema(project: Project) -> None:
    if not hasattr(project.assumptions, "outdoor_environment"):
        project.assumptions.outdoor_environment = DEFAULT_OUTDOOR_ENVIRONMENT
    if not hasattr(project.assumptions, "advanced_dust_override"):
        project.assumptions.advanced_dust_override = False
    if not project.assumptions.advanced_dust_override:
        profile = environment_profile(project.assumptions.outdoor_environment)
        project.assumptions.dust_concentration_mg_m3 = profile.dust_concentration_mg_m3
        project.assumptions.environment_factor = profile.environment_factor
    for scenario in project.scenarios:
        for stage in scenario.stages:
            if not hasattr(stage, "filter_id"):
                stage.filter_id = ""
            if not hasattr(stage, "width_mm"):
                stage.width_mm = 0.0
            if not hasattr(stage, "height_mm"):
                stage.height_mm = 0.0
            if not hasattr(stage, "media_area_m2"):
                stage.media_area_m2 = 0.0
            if not hasattr(stage, "eurovent_iso_group"):
                stage.eurovent_iso_group = "ISO ePM1"
            if not hasattr(stage, "eurovent_mx_g"):
                stage.eurovent_mx_g = 200.0
            if not hasattr(stage, "eurovent_curve"):
                stage.eurovent_curve = []


def stage_from_filter_record(
    record: FilterDatabaseRecord,
    outdoor_environment: str = DEFAULT_OUTDOOR_ENVIRONMENT,
) -> FilterStage:
    mass_efficiency, _source = effective_mass_efficiency(
        record.mass_efficiency,
        getattr(record, "epm1_percent", 0.0),
        getattr(record, "epm25_percent", 0.0),
        getattr(record, "epm10_percent", 0.0),
        getattr(record, "coarse_percent", 0.0),
        outdoor_environment,
        record.filter_class,
    )
    return FilterStage(
        stage=record.stage,
        qty_per_ahu=record.qty_per_ahu,
        dhc_g=record.dhc_g,
        mass_efficiency=mass_efficiency,
        avg_dp_pa=record.avg_dp_pa,
        price_vnd_filter=record.price_vnd_filter,
        width_mm=record.width_mm,
        height_mm=record.height_mm,
        media_area_m2=record.media_area_m2,
        filter_id=record.filter_id,
    )


def default_scenarios_from_filter_database(
    filter_database: list[FilterDatabaseRecord],
    outdoor_environment: str = DEFAULT_OUTDOOR_ENVIRONMENT,
) -> list[Scenario]:
    stage_order = ["Pre-filter", "Fine-filter", "EPA / Final-filter", "HEPA", "ULPA"]
    records_by_stage: dict[str, list[FilterDatabaseRecord]] = {}
    for record in filter_database:
        if record.filter_id.strip() and record.stage.strip():
            records_by_stage.setdefault(record.stage, []).append(record)

    base_records = [
        records_by_stage[stage][0]
        for stage in stage_order
        if stage in records_by_stage and records_by_stage[stage]
    ]
    if not base_records:
        return []

    scenarios = [
        Scenario(
            "Base / Current",
            [stage_from_filter_record(record, outdoor_environment) for record in base_records],
        )
    ]

    option_records = []
    has_alternative = False
    for record in base_records:
        stage_records = records_by_stage.get(record.stage, [record])
        selected = stage_records[-1]
        if selected.filter_id != record.filter_id:
            has_alternative = True
        option_records.append(selected)
    if has_alternative:
        scenarios.append(
            Scenario(
                "Option 1",
                [stage_from_filter_record(record, outdoor_environment) for record in option_records],
            )
        )
    return scenarios


def create_new_project() -> Project:
    project = default_project()
    saved_filter_database = load_filter_database()
    if saved_filter_database or DEFAULT_FILTER_DATABASE_PATH.exists():
        project.filter_database = saved_filter_database
    database_scenarios = default_scenarios_from_filter_database(
        project.filter_database,
        project.assumptions.outdoor_environment,
    )
    if database_scenarios:
        project.scenarios = database_scenarios
    now = datetime.now()
    project.project_info.project_name = f"New LCC Project {now:%Y-%m-%d %H:%M}"
    project.project_info.customer = ""
    project.project_info.location = ""
    project.project_info.date = now.strftime("%Y-%m-%d")
    project.calculation_results = {}
    return project


def set_project(project: Project) -> None:
    st.session_state.project = project
    st.session_state.comparison = compare_scenarios(project.scenarios, project.assumptions)


def reset_filter_database_editor() -> None:
    st.session_state.pop("filter_database_data", None)
    st.session_state.filter_database_nonce = st.session_state.get("filter_database_nonce", 0) + 1


def reset_project_info_editor() -> None:
    for key in [
        "project_info_project_name",
        "project_info_customer",
        "project_info_location",
        "project_info_engineer",
        "project_info_date",
        "project_info_currency",
    ]:
        st.session_state.pop(key, None)


def normalize_page_key(page: str | None) -> str:
    if page in MENU_KEYS:
        return str(page)
    if page in LEGACY_PAGE_KEYS:
        return LEGACY_PAGE_KEYS[str(page)]
    return "project"


def current_comparison(project: Project) -> dict[str, object]:
    warnings = validate_project(project.assumptions, project.scenarios)
    if warnings:
        comparison = {"summaries": [], "stages": [], "best_option": None}
        st.session_state.validation_warnings = warnings
        st.session_state.comparison = comparison
        return comparison
    comparison = compare_scenarios(project.scenarios, project.assumptions)
    st.session_state.comparison = comparison
    return comparison


def render_sidebar(project: Project) -> str:
    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), width="stretch")
    st.sidebar.markdown(
        '<div class="sidebar-title">LCC HVAC Filter</div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        '<div class="sidebar-subtitle">Life-cycle cost decision tool</div>',
        unsafe_allow_html=True,
    )
    info = project.project_info
    st.sidebar.markdown(
        f"""
        <div class="sidebar-project">
            <strong>{info.project_name}</strong><br>
            <small>{info.customer or "Customer not entered"} | {info.location or "Location not entered"}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )
    requested_page = st.session_state.pop("requested_page", None)
    if requested_page:
        st.session_state.active_page = normalize_page_key(requested_page)
    if normalize_page_key(st.session_state.get("active_page")) != st.session_state.get("active_page"):
        st.session_state.active_page = normalize_page_key(st.session_state.get("active_page"))
    page_key = st.sidebar.radio(
        "Workflow",
        MENU_KEYS,
        format_func=lambda key: MENU_LABELS[key],
        key="active_page",
    )
    st.sidebar.divider()
    if st.sidebar.button("New Project", width="stretch"):
        set_project(create_new_project())
        reset_project_info_editor()
        reset_filter_database_editor()
        st.session_state.requested_page = "setup"
        st.session_state.flash_message = "New project created. Please enter project information."
        st.rerun()
    if st.sidebar.button("Calculate", type="primary", width="stretch"):
        warnings = validate_project(project.assumptions, project.scenarios)
        if warnings:
            st.session_state.validation_warnings = warnings
        else:
            st.session_state.validation_warnings = []
        current_comparison(project)
    return page_key


def render_page_header(page_key: str) -> None:
    title, subtitle = PAGE_TITLES[page_key]
    st.markdown(
        f"""
        <div class="page-heading">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_project_context(project: Project, page: str) -> None:
    info = project.project_info
    customer = info.customer or "Not entered"
    location = info.location or "Not entered"
    page_label = MENU_LABELS.get(page, page)
    st.markdown(
        f"""
        <div class="project-context">
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-label">Project</div>
                    <div class="status-value">{info.project_name}</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Section</div>
                    <div class="status-value">{page_label}</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Customer</div>
                    <div class="status-value">{customer}</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Location</div>
                    <div class="status-value">{location}</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Currency</div>
                    <div class="status-value">{info.currency}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_validation(project: Project) -> bool:
    warnings = validate_project(project.assumptions, project.scenarios)
    st.session_state.validation_warnings = warnings
    if warnings:
        st.warning("Please review input warnings before using the result.")
        for warning in warnings:
            st.write(f"- {warning}")
        return False
    return True


def next_option_name(project: Project) -> str:
    existing = {scenario.name.strip().lower() for scenario in project.scenarios}
    option_number = 1
    while f"option {option_number}".lower() in existing:
        option_number += 1
    return f"Option {option_number}"


def add_option(project: Project) -> None:
    base = project.scenarios[0] if project.scenarios else Scenario("Base / Current", [])
    project.scenarios.append(copy_scenario(base, next_option_name(project)))
    set_project(project)
    st.session_state.flash_message = "New option added. Please review and adjust its filter stages."
    st.rerun()


def render_scenario_page(project: Project, index: int) -> None:
    scenario = project.scenarios[index]
    scenario_key = f"scenario_{index}"
    name_col, action_col = st.columns([4, 1])
    new_name = name_col.text_input(
        "Scenario name",
        value=scenario.name,
        disabled=index == 0,
        key=f"{scenario_key}_name",
    )
    if index == 0:
        scenario.name = "Base / Current"
    elif new_name.strip():
        scenario.name = new_name.strip()
    if index > 0 and action_col.button(
        "Remove Option",
        key=f"remove_option_{index}",
        width="stretch",
    ):
        removed_name = project.scenarios[index].name
        project.scenarios.pop(index)
        set_project(project)
        st.session_state.flash_message = f"{removed_name} removed from comparison."
        st.rerun()

    if index > 0:
        tools = st.columns(3)
        if tools[0].button(
            "Copy from Base",
            key=f"copy_base_{index}",
            width="stretch",
        ):
            project.scenarios[index] = copy_scenario(project.scenarios[0], scenario.name)
            set_project(project)
            st.rerun()
        previous_label = project.scenarios[index - 1].name if index > 1 else "Previous Option"
        if index > 1 and tools[1].button(
            f"Copy from {previous_label}",
            key=f"copy_option_1_{index}",
            width="stretch",
        ):
            project.scenarios[index] = copy_scenario(project.scenarios[index - 1], scenario.name)
            set_project(project)
            st.rerun()
        if tools[2].button(
            "Clear option",
            key=f"clear_option_{index}",
            width="stretch",
        ):
            project.scenarios[index].stages = []
            set_project(project)
            st.rerun()
    project.scenarios[index] = render_scenario_editor(
        project.scenarios[index],
        key_prefix=scenario_key,
        filter_database=project.filter_database,
        outdoor_environment=project.assumptions.outdoor_environment,
    )


def render_setup_section(project: Project) -> None:
    project_tab, assumptions_tab = st.tabs(["Project Info", "Operating Assumptions"])
    with project_tab:
        st.markdown('<div class="section-label">Step 1</div>', unsafe_allow_html=True)
        project.project_info = render_project_info(project.project_info)
    with assumptions_tab:
        st.markdown('<div class="section-label">Step 2</div>', unsafe_allow_html=True)
        project.assumptions = render_assumptions(project.assumptions)


def render_scenarios_section(project: Project) -> None:
    if not project.scenarios:
        project.scenarios.append(Scenario("Base / Current", []))
    tools = st.columns([1, 3])
    if tools[0].button("Add Option", type="primary", width="stretch"):
        add_option(project)
    tools[1].caption(
        "Add or remove options here. Every option is automatically included in Dashboard, TCO Model, Results, and Export."
    )

    tab_labels = [
        "Base Case" if index == 0 else scenario.name
        for index, scenario in enumerate(project.scenarios)
    ]
    tabs = st.tabs(tab_labels)
    for index, tab in enumerate(tabs):
        with tab:
            st.markdown(
                f'<div class="section-label">Scenario {index + 1}</div>',
                unsafe_allow_html=True,
            )
            render_scenario_page(project, index)


def render_analysis_section(project: Project, comparison: dict[str, object]) -> None:
    if not render_validation(project):
        return
    dashboard_tab, tco_tab, results_tab = st.tabs(
        ["Dashboard", "TCO Model", "Detailed Results"]
    )
    with dashboard_tab:
        st.markdown('<div class="section-label">Executive View</div>', unsafe_allow_html=True)
        render_dashboard(comparison, project.project_info.currency, LOGO_PATH)
    with tco_tab:
        st.markdown('<div class="section-label">Calculation Model</div>', unsafe_allow_html=True)
        render_tco_model(comparison, project.project_info.currency)
    with results_tab:
        st.markdown('<div class="section-label">Audit Tables</div>', unsafe_allow_html=True)
        render_results(comparison, project.project_info.currency)


def render_export(project: Project, comparison: dict[str, object]) -> None:
    st.subheader("Export")
    payload = project_to_payload(project)
    payload["calculation_results"] = comparison

    st.download_button(
        "Save Project JSON",
        data=json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"),
        file_name="LCC_Project.json",
        mime="application/json",
        width="stretch",
    )

    uploaded = st.file_uploader("Load Project JSON", type=["json"])
    if uploaded is not None:
        try:
            loaded = load_project_from_bytes(uploaded.getvalue())
            set_project(loaded)
            reset_project_info_editor()
            reset_filter_database_editor()
            st.success("Project loaded. The interface has been updated.")
            st.rerun()
        except Exception as exc:
            st.error(f"Cannot load project file: {exc}")

    try:
        excel_bytes = build_excel_report(project)
        st.download_button(
            "Export Excel Report",
            data=excel_bytes,
            file_name="LCC_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
    except Exception as exc:
        st.error(f"Cannot build Excel report: {exc}")

    if st.button("Reset Input", width="stretch"):
        set_project(create_new_project())
        reset_project_info_editor()
        reset_filter_database_editor()
        st.session_state.requested_page = "setup"
        st.session_state.flash_message = "Input reset. A fresh project is ready."
        st.rerun()


def main() -> None:
    setup_page()
    project = get_project()
    project.project_info = sync_project_info_from_session(project.project_info)
    page_key = render_sidebar(project)
    render_page_header(page_key)
    render_project_context(project, page_key)
    if "flash_message" in st.session_state:
        st.success(st.session_state.pop("flash_message"))

    if page_key == "setup":
        render_setup_section(project)
    elif page_key == "filter_data":
        project.filter_database = render_filter_database(project.filter_database)
    elif page_key == "scenarios":
        render_scenarios_section(project)

    comparison = current_comparison(project)
    project.calculation_results = comparison

    if page_key == "analysis":
        render_analysis_section(project, comparison)
    elif page_key == "export":
        render_validation(project)
        render_export(project, comparison)


if __name__ == "__main__":
    main()
