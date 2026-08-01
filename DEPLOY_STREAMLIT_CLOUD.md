# Deploy LCC HVAC App Online

Use this guide when you want customers or managers to open the app from a browser link without installing Python, VS Code, or packages.

## Recommended Public Link Setup

1. Push this repository to GitHub.
2. Go to `https://share.streamlit.io`.
3. Create a new app.
4. Select your GitHub repository and branch.
5. Use this app entrypoint:

```text
streamlit_app.py
```

6. In Advanced settings, use Python 3.12.
7. Deploy.

Streamlit Cloud will install dependencies from the root `requirements.txt`.

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
