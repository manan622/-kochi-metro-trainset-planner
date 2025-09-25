@echo off
title Kochi Metro Trainset Planner - Development Environment

echo ============================================================
echo 🚀 Kochi Metro Trainset Induction Planner - Dev Starter
echo ============================================================

echo.
echo 📂 Checking current directory...
cd /d "%~dp0"

echo.
echo 🔍 Checking prerequisites...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
) else (
    echo ✅ Python is available
)

npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js/NPM is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
) else (
    echo ✅ Node.js/NPM is available
)

echo.
echo 🔧 Starting Backend Server...
start "Backend Server" /D "backend" cmd /c "uvicorn main:app --host 0.0.0.0 --port 8001 --reload || pause"

echo.
echo 🌐 Starting Frontend Server...
start "Frontend Server" /D "frontend" cmd /c "npm start || pause"

echo.
echo ============================================================
echo ✨ Both servers are now starting!
echo    Backend:  http://localhost:8001
echo    Frontend: http://localhost:3000
echo.
echo 📝 Keep this window open while developing
echo    Close this window to stop both servers
echo ============================================================

echo.
echo Press any key to close this window and stop the servers...
pause >nul