@echo off
title TrueNexus by TrueScent
cd /d "%~dp0"
python -m truenexus
if errorlevel 1 (
  echo.
  echo Failed to start. Install deps:  pip install -r requirements.txt
  pause
)
