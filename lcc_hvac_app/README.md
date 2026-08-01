# LCC HVAC Filter System

Python application for calculating Life Cycle Cost / Total Cost of Ownership for HVAC/AHU filter systems.

The project follows the requirements in `LCC_HVAC_Filter_Software_Tong_Hop.md`:

- Direct user input for Base/Current and Option scenarios.
- Independent Python calculation engine, not Excel cell references.
- Filter life, replacement/year, filter cost, energy cost, labor/disposal cost, CO2, and TCO.
- Scenario comparison against Base/Current.
- Streamlit dashboard with charts and KPI metrics.
- Save/load project as JSON.
- Export Excel report with summary, assumptions, scenario inputs, results, chart data, and formula reference.

## Folder Structure

```text
lcc_hvac_app/
  app.py
  engine/
    dust.py
    filter_life.py
    energy.py
    cost.py
    co2.py
    tco.py
    scenario.py
    validation.py
    models.py
  ui/
  export/
  project_io/
  sample_projects/
  tests/
```

## Install

The included run scripts create the local environment automatically.

## Run

On Windows, double-click:

```text
lcc_hvac_app/run_app.bat
```

On MacBook, run once:

```bash
chmod +x lcc_hvac_app/run_app_mac.command
```

Then double-click:

```text
lcc_hvac_app/run_app_mac.command
```

The first run needs internet access to install `uv`, Python, and package requirements.

## Deploy Online

For a public browser link with Streamlit Community Cloud, use the root `streamlit_app.py` entrypoint and follow:

```text
../DEPLOY_STREAMLIT_CLOUD.md
```

The online Filter Data page supports uploading an Excel filter database, editing records, and downloading an updated Excel file.

## Test

```bash
python -m pytest lcc_hvac_app/tests
```

If `pytest` is not installed, install the requirements first.

## Calculation Notes

Mass efficiency can be entered as decimal (`0.85`) or percent (`85`). The engine normalizes values greater than `1` by dividing by `100`.

Energy cost is calculated per filter stage using the stage average pressure drop. The stage energy values are summed for scenario totals.
