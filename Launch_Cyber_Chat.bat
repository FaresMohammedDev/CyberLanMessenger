@echo off
title CYBER-CHAT // INITIALIZING P2P NODE
color 0B
cls
echo ========================================================
echo   [+] LAUNCHING CYBER-CHAT P2P SECRET LAN MESH...
echo ========================================================
python "%~dp0cyber_chat.py"
if %errorlevel% neq 0 (
    echo.
    echo [!] An error occurred. Press any key to exit...
    pause >nul
)
