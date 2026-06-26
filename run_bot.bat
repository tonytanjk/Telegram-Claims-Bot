@echo off
title Telegram Bot - Portable Edition
setlocal enabledelayedexpansion

echo ================================================
echo   TELEGRAM BOT - PORTABLE EDITION
echo ================================================
echo.
echo This package does NOT require Python installation!
echo Uses embedded Python distribution
echo.

REM Get current directory
set "BOT_DIR=%~dp0"
set "BOT_DIR=%BOT_DIR:~0,-1%"

REM Set Python paths for Windows 11 compatibility
set "PYTHON_EXE=%BOT_DIR%\python\python.exe"
set "PYTHONPATH=%BOT_DIR%;%BOT_DIR%\python\Lib\site-packages;%BOT_DIR%\python\Lib"
set "PYTHONHOME=%BOT_DIR%\python"

REM Change to bot directory to ensure relative imports work
cd /d "%BOT_DIR%"
set "PATH=%BOT_DIR%\python;%BOT_DIR%\python\Scripts;%PATH%"

REM Change to bot directory to ensure relative imports work
cd /d "%BOT_DIR%"

echo Bot directory: %BOT_DIR%
echo Python executable: %PYTHON_EXE%
echo.

REM Check if embedded Python exists
if not exist "%PYTHON_EXE%" (
    echo ❌ ERROR: Embedded Python not found: %PYTHON_EXE%
    echo Make sure the python folder is in the same directory
    pause
    exit /b 1
)

echo ✅ SUCCESS: Embedded Python found

REM Check for bot script
if not exist "%BOT_DIR%\bot.py" (
    echo ❌ ERROR: Bot script not found: %BOT_DIR%\bot.py
    pause
    exit /b 1
)

echo ✅ SUCCESS: Bot script found

REM Check for OAuth credentials
if not exist "%BOT_DIR%\oauth_credentials.json" (
    echo ❌ ERROR: OAuth credentials not found
    echo Make sure oauth_credentials.json is in this directory
    pause
    exit /b 1
)

echo ✅ SUCCESS: OAuth credentials found
echo.

REM Start the bot with proper environment
echo 🚀 Starting Telegram Bot...
echo 🛑 Press Ctrl+C to stop
echo.

REM Run from bot directory with environment set - use relative path
python\python.exe start_bot.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Bot exited with error code: %ERRORLEVEL%
    echo Check the error messages above
    pause
) else (
    echo.
    echo ✅ Bot stopped normally
)
