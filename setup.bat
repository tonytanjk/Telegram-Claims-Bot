@echo off
echo Setting up Telegram Expense Claims Bot...
echo.

REM Check if config files exist
if not exist "config.py" (
    echo Copying example configuration files...
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
echo ⚠️  IMPORTANT: Please edit the following files with your settings:
echo    • config.py - Add your bot token, admin usernames, and Google Drive folder ID
echo    • oauth_credentials.json - Add your Google OAuth credentials
echo    • data\admin_users.json - Add your admin usernames
echo    • data\allowed_users.json - Add allowed user list
echo.
echo 📖 See README.md for detailed setup instructions.
echo.
pause
