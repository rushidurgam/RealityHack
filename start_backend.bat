@echo off
title SkillBridge AI - Backend API
echo ============================================================
echo Starting SkillBridge AI FastAPI Backend (Port 8000)...
echo ============================================================
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
