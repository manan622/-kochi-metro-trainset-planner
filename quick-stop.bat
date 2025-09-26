@echo off
:: Quick Stop for Kochi Metro Trainset Planner
taskkill /F /IM python.exe /FI "COMMANDLINE eq *uvicorn*" 2>nul
taskkill /F /IM node.exe /FI "COMMANDLINE eq *react-scripts*" 2>nul
taskkill /F /IM cmd.exe /FI "WINDOWTITLE eq Backend Server*" 2>nul
taskkill /F /IM cmd.exe /FI "WINDOWTITLE eq Frontend Server*" 2>nul
echo Servers stopped.
timeout /t 2 /nobreak >nul
exit