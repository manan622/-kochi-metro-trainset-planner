@echo off
title Kochi Metro Trainset Planner - Shutdown
color 0C

echo ====================================================
echo    Kochi Metro Trainset Planner - Stopping...
echo ====================================================
echo.

:: Kill Backend Server (FastAPI/Uvicorn)
echo [STEP 1/3] Stopping Backend Server...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend Server*" 2>nul
taskkill /F /IM python.exe /FI "COMMANDLINE eq *uvicorn*" 2>nul
if errorlevel 1 (
    echo [INFO] No backend server processes found
) else (
    echo [SUCCESS] Backend server stopped
)

:: Kill Frontend Server (Node.js/React)
echo [STEP 2/3] Stopping Frontend Server...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq Frontend Server*" 2>nul
taskkill /F /IM node.exe /FI "COMMANDLINE eq *react-scripts*" 2>nul
if errorlevel 1 (
    echo [INFO] No frontend server processes found
) else (
    echo [SUCCESS] Frontend server stopped
)

:: Close any remaining command windows
echo [STEP 3/3] Cleaning up...
taskkill /F /IM cmd.exe /FI "WINDOWTITLE eq Backend Server*" 2>nul
taskkill /F /IM cmd.exe /FI "WINDOWTITLE eq Frontend Server*" 2>nul

echo.
echo ====================================================
echo    Application Stopped Successfully!
echo ====================================================
echo.
echo All servers have been shut down.
echo You can now safely close this window.
echo.
echo To restart the application, run:
echo - start-app.bat (full startup with info)
echo - quick-start.bat (silent startup)
echo.
echo Press any key to exit...
pause >nul