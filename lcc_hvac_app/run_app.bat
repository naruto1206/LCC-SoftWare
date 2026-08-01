@echo off
setlocal
cd /d "%~dp0"

set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"

where uv >nul 2>nul
if errorlevel 1 (
    echo Installing uv for this Windows user...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python environment...
    uv venv .venv --python 3.12
    if errorlevel 1 (
        echo Failed to create Python environment.
        pause
        exit /b 1
    )
)

echo Installing or updating required packages...
uv pip install --python ".venv\Scripts\python.exe" -r requirements.txt
if errorlevel 1 (
    echo Failed to install required packages.
    pause
    exit /b 1
)

echo Starting LCC HVAC Filter System...
start "" "http://localhost:8501"
".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501
