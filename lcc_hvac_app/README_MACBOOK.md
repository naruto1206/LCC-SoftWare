# Run LCC HVAC Filter System On MacBook

## First Time

1. Unzip the package.
2. Open the unzipped folder.
3. Open Terminal in this folder.
4. Run:

```bash
chmod +x lcc_hvac_app/run_app_mac.command
```

5. Double-click:

```text
lcc_hvac_app/run_app_mac.command
```

The app will open at:

```text
http://localhost:8501
```

## What The Script Does

- Checks if `uv` is installed.
- Installs `uv` for the current user if needed.
- Creates a local Python environment inside `lcc_hvac_app/.venv`.
- Installs the required packages.
- Starts the Streamlit app.

The first run needs internet access because packages must be downloaded. Later runs are faster.

## Important

Keep these items together in the same parent folder:

```text
lcc_hvac_app/
Logo AIR FILTECH_FA-01.jpg
```

The app does not need VS Code. VS Code is only needed if someone wants to edit the source code.
