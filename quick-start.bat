@echo off
:: Quick Start for Kochi Metro Trainset Planner
cd /d "%~dp0"
start /min cmd /c "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001"
timeout /t 5 /nobreak >nul
start /min cmd /c "cd frontend && npm start"
timeout /t 10 /nobreak >nul
start http://localhost:3000
exit
title Kochi Metro - Quick Start

:: Change to the project directory
cd /d "%~dp0"

:: Start both servers minimized
start "Backend" /min cmd /c "cd backend && python main.py"
start "Frontend" /min cmd /c "cd frontend && npm start"

:: Wait and open browser
timeout /t 8 /nobreak >nul
start http://localhost:3000

:: Show status
echo ============================================================
echo 🚂 Kochi Metro Trainset Planner - RUNNING
echo ============================================================
echo.
echo ✅ Application started successfully!
echo 🌍 URL: http://localhost:3000
echo.
echo 👥 Login Credentials:
echo    Management: admin / admin123
echo    Inspector:  inspector1 / inspector123
echo    Worker:     worker1 / worker123
echo.
echo Press any key to close this window...
echo (Servers will continue running)
pause >nul