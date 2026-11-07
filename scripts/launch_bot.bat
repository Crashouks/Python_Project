@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch_bot.ps1"
if errorlevel 1 (
    echo.
    echo The Telegram bot launcher failed. See the message above.
    pause
)
