@echo off
title CYBER-LAN SUPER SUITE v3.0 // INITIALIZING
color 0A
cls
echo ========================================================
echo   [+] LAUNCHING CYBER-LAN SUPER SUITE (DISCORD EDITION)
echo   [+] Database, Watch Party, Games, Stories, Files...
echo ========================================================
python "%~dp0cyber_super_suite.py"
if %errorlevel% neq 0 (
    echo.
    echo [!] An error occurred. Press any key to exit...
    pause >nul
)
