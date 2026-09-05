# Path To Put This Project Online

Goal: upload the app to GitHub and deploy it on Streamlit Community Cloud so users can open it from a web link without installing Python, VS Code, or any packages.

## 1. Use The GitHub-Ready Package

Use this prepared folder or zip:

```text
dist/LCC_HVAC_Filter_GitHub_Ready.zip
```

Upload the contents of this zip to GitHub.

Do not upload:

```text
.venv/
dist/
*.rar
*.zip
*.log
__pycache__/
.pytest_cache/
```

## 2. Create GitHub Repository

1. Go to:

```text
https://github.com/new
```

2. Repository name suggestion:

```text
lcc-hvac-filter-app
```

3. Choose `Private` or `Public`.
4. Click `Create repository`.

## 3. Upload Files To GitHub

In the empty GitHub repository:

1. Click `uploading an existing file`.
2. Drag and drop all contents from:

```text
dist/LCC_HVAC_Filter_GitHub_Ready/
```

3. Commit message:

```text
Initial Streamlit app deployment
```

4. Click `Commit changes`.

Your GitHub repository root must contain:

```text
streamlit_app.py
requirements.txt
.streamlit/config.toml
lcc_hvac_app/
Logo AIR FILTECH_FA-01.jpg
```

## 4. Deploy On Streamlit Community Cloud

1. Go to:

```text
https://share.streamlit.io
```

2. Sign in with GitHub.
3. Click `Create app`.
4. Choose:

```text
Repository: your GitHub repository
Branch: main
Main file path: streamlit_app.py
```

5. Open `Advanced settings`.
6. Choose Python version:

```text
3.12
```

7. Click `Deploy`.

## 5. Share The Online Link

After deployment, Streamlit will give a link like:

```text
https://your-app-name.streamlit.app
```

Send that link to users. They only need a browser.

## 6. Create Two Separate Online Apps

If you want one link for the DHC-based app and one link for the Filter-life-based app, create two Streamlit Cloud apps from the same GitHub repository.

### Link 1: DHC-Based App

Create a Streamlit Cloud app with:

```text
Repository: naruto1206/LCC-SoftWare
Branch: full-app
Main file path: streamlit_dhc_app.py
```

Suggested app URL:

```text
lcc-dhc-based
```

### Link 2: Filter-Life-Based App

Create another Streamlit Cloud app with:

```text
Repository: naruto1206/LCC-SoftWare
Branch: full-app
Main file path: streamlit_filter_life_app.py
```

Suggested app URL:

```text
lcc-filter-life-based
```

After this, Streamlit Cloud will give two different links. The second app will not appear automatically inside the first app. It must be created as a separate Streamlit Cloud app.

## 7. Update The App Later

To update the online app:

1. Edit files locally.
2. Upload changed files to GitHub.
3. Streamlit Community Cloud will redeploy automatically.

## If You Want Codex To Upload Files

Give Codex:

```text
GitHub repository full name: username/repository-name
```

Example:

```text
airfiltech/lcc-hvac-filter-app
```

Then Codex can help create/update text files in that existing repository.
