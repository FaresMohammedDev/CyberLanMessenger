@echo off
title CYBER-LAN INJECTOR // INITIALIZING
color 0A
cls
echo ========================================================
echo   [+] STARTING CYBER-LAN INJECTOR ^& RADAR SCANNER...
echo ========================================================
python "%~dp0cyber_messenger.py"
if %errorlevel% neq 0 (
    echo.
    echo [!] An error occurred. Press any key to exit...
    pause >nul
)
