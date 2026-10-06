#!/usr/bin/env sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if [ ! -x .venv/bin/python ]; then
  python3.12 -m venv .venv
fi
if [ ! -f .venv/careerlens-ready ]; then
  .venv/bin/python -m pip install -r requirements.txt
  touch .venv/careerlens-ready
fi
exec .venv/bin/python -m streamlit run app.py
