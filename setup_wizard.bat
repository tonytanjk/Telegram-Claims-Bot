@echo off
echo ===================================================
echo    Telegram Expense Claims Bot - Setup Wizard
echo ===================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Install required packages
echo 📦 Installing required packages...
pip install python-telegram-bot google-api-python-client google-auth-httplib2 google-auth-oauthlib pywin32

if errorlevel 1 (
    echo ❌ Failed to install packages
    pause
    exit /b 1
)

echo ✅ Packages installed successfully
echo.

REM Create data directory
if not exist "data" mkdir data

REM Check if this is first time setup
if exist "config.py" (
    echo 🔧 Configuration files already exist
    echo Choose an option:
    echo   1. Run Configurator GUI
    echo   2. Reconfigure from scratch
    echo   3. Exit
    echo.
    set /p choice="Enter your choice (1-3): "
    
    if "%choice%"=="1" (
        echo Starting configurator...
        python configurator.py
        goto :end
    )
    if "%choice%"=="2" (
        echo Backing up existing config...
        if exist "config.py" copy config.py config.py.backup
        if exist "oauth_credentials.json" copy oauth_credentials.json oauth_credentials.json.backup
        goto :first_time_setup
    )
    if "%choice%"=="3" (
        goto :end
    )
    echo Invalid choice, running configurator...
    python configurator.py
    goto :end
)

:first_time_setup
echo 🎯 First time setup detected
echo.

REM Copy example files
echo Creating configuration files...

if not exist "config.py" (
    copy config_example.py config.py
    echo ✅ Created config.py
)

if not exist "oauth_credentials.json" (
    copy oauth_credentials_example.json oauth_credentials.json
    echo ✅ Created oauth_credentials.json
)

if not exist "data\admin_users.json" (
    copy data\admin_users_example.json data\admin_users.json
    echo ✅ Created data\admin_users.json
)

if not exist "data\allowed_users.json" (
    copy data\allowed_users_example.json data\allowed_users.json
    echo ✅ Created data\allowed_users.json
)

echo.
echo 🚀 Setup completed! 
echo.
echo Next steps:
echo   1. Run the configurator: python configurator.py
echo   2. Or manually edit the configuration files:
echo      • config.py - Add your bot token and settings
echo      • oauth_credentials.json - Add Google OAuth credentials
echo      • data\admin_users.json - Add admin usernames
echo      • data\allowed_users.json - Add allowed users
echo.
echo 💡 The configurator provides an easy GUI interface for all settings!
echo.

REM Ask if user wants to open configurator
set /p open_config="Open configurator now? (y/n): "
if /i "%open_config%"=="y" (
    echo Starting configurator...
    python configurator.py
)

:end
echo.
echo 📖 See README.md for detailed instructions
echo 🔧 Use 'python configurator.py' anytime to modify settings
echo.
pause
