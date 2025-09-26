@echo off
title Kochi Metro Trainset Planner - Startup
color 0A

echo ====================================================
echo    Kochi Metro Trainset Planner - Starting...
echo ====================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo [INFO] Dependencies check passed
echo.

:: Navigate to project directory
cd /d "%~dp0"

:: Start Backend Server
echo [STEP 1/3] Starting Backend Server...
start /min "Backend Server" cmd /c "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001"

:: Wait for backend to start
echo [INFO] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

:: Start Frontend Server
echo [STEP 2/3] Starting Frontend Server...
start /min "Frontend Server" cmd /c "cd frontend && npm start"

:: Wait for frontend to start
echo [INFO] Waiting for frontend to initialize...
timeout /t 10 /nobreak >nul

:: Open Application in Browser
echo [STEP 3/3] Opening Application in Browser...
start http://localhost:3000

echo.
echo ====================================================
echo    Application Started Successfully!
echo ====================================================
echo.
echo Backend Server: http://localhost:8001
echo Frontend App:   http://localhost:3000
echo API Docs:       http://localhost:8001/docs
echo.
echo Login Credentials:
echo - Management: admin / admin123
echo - Inspector:  inspector / inspect123
echo - Worker:     worker / worker123
echo.
echo Features Available:
echo - Inspection Management
echo - Trainset Management
echo - Fleet Overview
echo - Scalable Data Entry
echo - Dummy Data Generation
echo.
echo Press any key to exit this window...
echo (Backend and Frontend will continue running)
pause >nul