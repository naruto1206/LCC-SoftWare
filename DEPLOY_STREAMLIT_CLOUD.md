# Deploy LCC HVAC App Online

Use this guide when you want customers or managers to open the app from a browser link without installing Python, VS Code, or packages.

## Recommended Public Link Setup

1. Push this repository to GitHub.
2. Go to `https://share.streamlit.io`.
3. Create a new app.
4. Select your GitHub repository and branch.
5. Use this app entrypoint for the combined app:

```text
streamlit_app.py
```

6. In Advanced settings, use Python 3.12.
7. Deploy.

Streamlit Cloud will install dependencies from the root `requirements.txt`.

## Two Separate App Links

This project also has two separate Streamlit entry files. Use these when you want two clean apps instead of one app with a calculation-version selector.

### App 1: DHC-Based LCC

Create one Streamlit Cloud app with this main file:

```text
streamlit_dhc_app.py
```

This app is locked to the DHC-based calculation. It uses DHC, dust concentration, outdoor environment, mass efficiency, pressure drop, filter price, labor/disposal cost, electricity price, operating hours, and fan efficiency.

### App 2: Filter-Life-Based LCC

Create another Streamlit Cloud app with this main file:

```text
streamlit_filter_life_app.py
```

This app is locked to the filter-life-based calculation. It uses the target filter life entered for each filter record instead of calculating life from DHC.

After deployment, Streamlit Cloud will give you two different URLs, one for each app. Both apps can use the same GitHub repository and branch.

## Filter Database Workflow Online

The online app supports this Excel workflow:

1. Open the public Streamlit link.
2. Go to `Filter Data`.
3. Upload a filter database `.xlsx` file.
4. Import the `Filter_Database` sheet.
5. Add, update, or delete filter records in the app.
6. Download the updated file with `Download database Excel`.

This is good when each user works with their own Excel file.

## Important Limit

Streamlit Community Cloud does not behave like a permanent shared file server. If a user edits the Filter Database in the app, that change is reliable for their current session and can be downloaded as Excel. It is not a safe way to permanently modify the GitHub `.xlsx` file for every user.

For a shared company-wide database where every user edits the same live Filter Database, connect one of these:

- Google Sheets
- Supabase
- PostgreSQL
- Airtable
- Microsoft SharePoint / OneDrive through an API

## Files Needed For Deployment

Keep these files in GitHub:

```text
streamlit_app.py
streamlit_dhc_app.py
streamlit_filter_life_app.py
requirements.txt
.streamlit/config.toml
lcc_hvac_app/
```

Do not upload local runtime folders:

```text
lcc_hvac_app/.venv/
lcc_hvac_app/.python/
lcc_hvac_app/.uv-cache/
```

They are already ignored by `.gitignore`.
