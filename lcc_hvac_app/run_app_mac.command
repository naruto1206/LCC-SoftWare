#!/bin/bash
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv for this user..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Creating Python environment..."
  uv venv .venv --python 3.12
fi

echo "Installing or updating required packages..."
uv pip install --python .venv/bin/python -r requirements.txt

echo "Starting LCC HVAC Filter System..."
open "http://localhost:8501" >/dev/null 2>&1 || true
.venv/bin/streamlit run app.py --server.port 8501
