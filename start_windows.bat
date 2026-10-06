@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 (
    echo Install Python 3.12 from python.org, then run this file again.
    pause
    exit /b 1
  )
)
if not exist ".venv\careerlens-ready" (
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Dependency installation failed. Check your internet connection and retry.
    pause
    exit /b 1
  )
  echo ready>".venv\careerlens-ready"
)
.venv\Scripts\python.exe -m streamlit run app.py
if errorlevel 1 pause
