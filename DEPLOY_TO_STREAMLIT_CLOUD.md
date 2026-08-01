# Deploy To GitHub + Streamlit Community Cloud

This project is prepared for Streamlit Community Cloud.

## Files Community Cloud Needs

Keep these files/folders in GitHub:

```text
streamlit_app.py
requirements.txt
.streamlit/config.toml
lcc_hvac_app/
Logo AIR FILTECH_FA-01.jpg
```

Do not upload local environment/build files:

```text
lcc_hvac_app/.venv/
dist/
*.rar
*.zip
*.log
```

These are already excluded by `.gitignore`.

## GitHub Steps

1. Create a new GitHub repository.
2. Upload/push this project folder to the repository.
3. Make sure `streamlit_app.py` and `requirements.txt` are in the repository root.

## Streamlit Community Cloud Steps

1. Go to:

```text
https://share.streamlit.io
```

2. Sign in with GitHub.
3. Click `Create app`.
4. Choose your repository and branch.
5. Set the app file/entrypoint to:

```text
streamlit_app.py
```

6. In Advanced settings, use Python `3.12` if available.
7. Click `Deploy`.

After deployment, Streamlit will give you a public `streamlit.app` URL.

## Notes

The first deployment can take a few minutes while packages are installed.

When you update the GitHub repository, Streamlit Community Cloud will redeploy the app automatically.
