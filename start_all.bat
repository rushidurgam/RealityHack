@echo off
title SkillBridge AI Launcher
echo ============================================================
echo Launching SkillBridge AI (Backend + Modern Frontend)...
echo ============================================================
start "SkillBridge Backend" cmd /c "call "%~dp0start_backend.bat""
timeout /t 2 /nobreak >nul
start "SkillBridge Frontend" cmd /c "call "%~dp0start_frontend.bat""
echo.
echo [SkillBridge AI] System is starting up:
echo  - Backend API: http://127.0.0.1:8000 (Docs: http://127.0.0.1:8000/docs)
echo  - Modern UI:   http://127.0.0.1:5173
echo ============================================================
