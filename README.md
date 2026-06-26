# Telegram Expense Claims Bot 🤖💰

A portable Telegram bot for expense claim management with Google Sheets integration, admin controls, and Windows service support.

## ✨ What this project includes

- Telegram expense claim submission
- Admin approval workflow
- Google Sheets and Drive integration
- OAuth 2.0 authentication support
- Windows service installer and controller
- GUI configuration tool
- Audit logging and debugging support

## 🚀 Recommended Setup

### Option 1: Setup Wizard (Recommended)
1. Open PowerShell or Command Prompt as Administrator
2. Run `setup_wizard.bat`
3. Follow the prompts to install dependencies and create default config files
4. Open `python configurator.py` to finish configuration if needed

### Option 2: Manual Setup
1. Install Python 3.8+ from https://python.org
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Copy template configuration files:
   ```powershell
   copy config_example.py config.py
   copy oauth_credentials_example.json oauth_credentials.json
   copy data\admin_users_example.json data\admin_users.json
   copy data\allowed_users_example.json data\allowed_users.json
   ```
4. Edit `config.py`, `oauth_credentials.json`, `data/admin_users.json`, and `data/allowed_users.json`
5. Run the bot with `python bot.py`, `python start_bot.py`, or `run_bot.bat`

## 🔧 Configuration Files

### `config.py`
This file contains the main bot configuration values.

Example:
```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
BOT_NAME = "Expense Claims Bot"
DRIVE_FOLDER_ID = "1AbCdEfGhIjKlMnOpQrStUvWxYz"
SHEET_TYPE = "expense_tracker"
DEFAULT_CURRENCY = "USD"
TIMEZONE = "UTC"
```

### `oauth_credentials.json`
Google OAuth 2.0 credentials for your desktop application.

### `data/admin_users.json`
Admin Telegram usernames.

Example:
```json
["admin_username1", "admin_username2"]
```

### `data/allowed_users.json`
Allowed Telegram usernames.

Example:
```json
["user1", "user2", "user3"]
```

## 📝 Running the Bot

### Run directly
```powershell
python bot.py
```

### Run via the launcher
```powershell
python start_bot.py
```

### Run using portable batch helper
```powershell
run_bot.bat
```

## 🖥️ Windows Service Commands

### Install service
```powershell
python service_installer.py install
```

### Start service
```powershell
python service_installer.py start
```

### Stop service
```powershell
python service_installer.py stop
```

### Restart service
```powershell
python service_installer.py restart
```

### Check status
```powershell
python service_installer.py status
```

## 📱 Bot Commands

### User commands
- `/start` — Start the bot and show available commands
- `/claim` — Submit a new expense claim
- `/history` — View recent claims
- `/cancel` — Cancel the current operation

### Admin commands
- `/summary` — View expense summary
- `/download` — Download expense data
- `/dashboard` — Open admin dashboard
- `/adduser` — Add allowed user
- `/removeuser` — Remove allowed user
- `/listusers` — List allowed users
- `/addadmin` — Add admin user
- `/removeadmin` — Remove admin user
- `/listadmins` — List admin users
- `/pending` — View pending approvals
- `/cleanup` — Clean up old receipts
- `/auditlog` — Download the audit log
- `/listsheets` — List available Google Sheets

## 📁 Project Structure

```
telegram_bot_portable_final/
├── bot.py
├── configurator.py
├── service_installer.py
├── setup_wizard.bat
├── start_bot.py
├── run_bot.bat
├── run_bot.ps1
├── config.py
├── config_example.py
├── oauth_credentials.json
├── oauth_credentials_example.json
├── requirements.txt
├── README.md
├── data/
│   ├── admin_users.json
│   ├── allowed_users.json
│   ├── audit.log
│   └── receipts/
├── handlers/
├── services/
└── utils/
```

## 🛠️ Troubleshooting

### Bot startup issues
- Confirm `config.py` exists and contains a valid `BOT_TOKEN`
- Verify `DRIVE_FOLDER_ID` is set if Google Sheets integration is enabled
- Make sure `oauth_credentials.json` is present and valid JSON
- Check `bot.log` for errors
- Run `python bot.py` directly to see startup output

### Google Sheets / OAuth issues
- Ensure Google Sheets API and Drive API are enabled in Google Cloud
- Verify OAuth credentials match your desktop app configuration
- Confirm the Drive folder is accessible from the OAuth user
- Check for permission or scope errors in logs

### Windows service issues
- Run installation commands as Administrator
- Verify `pywin32` is installed
- Check `service.log` for service errors
- Use `python service_installer.py status` to inspect service state

### Permissions and file problems
- Ensure repository files and `data/` folder are writable
- Confirm `data/admin_users.json` and `data/allowed_users.json` contain valid arrays
- If using the portable Python runtime, make sure the `python/` folder exists and contains `python.exe`

### Common fixes
- Re-run `setup_wizard.bat` if configuration is missing or invalid
- Use `python configurator.py` for guided configuration
- Restart the bot or service after changing `config.py`
- Inspect `bot.log` and `service.log` for the root cause

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

**Made with ❤️ for expense management automation**

A powerful Telegram bot for managing expense claims with Google Sheets integration and admin approval workflows.

## ✨ Features

- � **Expense Claim Submission** - Users can submit claims with descriptions, amounts, and receipt photos
- 👑 **Admin Approval System** - Admins can approve/reject claims with reasons
- 📊 **Google Sheets Integration** - Automatic data sync to Google Sheets
- 🔐 **User Management** - Add/remove users and admins
- 📈 **Dashboard & Reports** - View summaries, history, and audit logs
- 🚀 **Portable** - Includes embedded Python runtime (no installation required)

## 🚀 Quick Setup

### 1. Download & Extract
1. Download this repository
2. Extract to your desired location

### 2. Get Your Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Copy your bot token

### 3. Set Up Google Sheets Integration
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable Google Sheets API and Google Drive API
4. Create credentials (OAuth 2.0 Client ID for Desktop Application)
5. Download the credentials JSON file

### 4. Configure the Bot

#### Option A: Copy Example Files (Recommended)
```batch
copy config_example.py config.py
copy oauth_credentials_example.json oauth_credentials.json
copy data\admin_users_example.json data\admin_users.json
copy data\allowed_users_example.json data\allowed_users.json
```

#### Option B: Set Environment Variables
```batch
set BOT_TOKEN=your_bot_token_here
set ADMIN_USERNAMES=your_username,another_admin
set DRIVE_FOLDER_ID=your_google_drive_folder_id
set SPREADSHEET_NAME=MY_EXPENSE_CLAIMS
```

### 5. Edit Configuration Files

#### Edit `config.py`:
```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
ADMIN_USERNAMES = {"your_telegram_username"}
DRIVE_FOLDER_ID = "1ABcDeFgHiJkLmNoPqRsTuVwXyZ"
SPREADSHEET_NAME = "My Expense Claims"
```

#### Edit `oauth_credentials.json`:
Replace the placeholder values with your Google OAuth credentials:
```json
{
  "installed": {
    "client_id": "your_google_client_id",
    "project_id": "your_project_id",
    "client_secret": "your_google_client_secret",
    ...
  }
}
```

#### Edit `data/admin_users.json`:
```json
["your_telegram_username", "another_admin_username"]
```

#### Edit `data/allowed_users.json`:
```json
["user1", "user2", "user3"]
```

### 6. Run the Bot

#### Windows (Recommended):
```batch
run_bot.bat
```

#### PowerShell:
```powershell
.\run_bot.ps1
```

#### Manual:
```batch
python\python.exe bot.py
```
- **No additional software needed**

## 📖 User Guide

### For Users:
- `/claim` - Submit a new expense claim
- `/summary` - View your total claims
- `/history` - View your recent claims
- `/cancel` - Cancel current operation

### For Admins:
- All user commands (auto-approved)
- `/pending` - View pending approvals
- `/adduser` / `/removeuser` - Manage users
- `/addadmin` / `/removeadmin` - Manage admins
- `/listusers` / `/listadmins` - View users/admins
- `/download` - Download expense data as Excel
- `/dashboard` - Access admin dashboard
- `/auditlog` - Download audit log
- `/cleanup` - Clean old files

## 🔧 Customization

### Changing Commands
Edit the `USER_COMMANDS` and `ADMIN_COMMANDS` in `config.py`:

```python
USER_COMMANDS = [
    ("claim", "📝 Submit expense"),
    ("mystatus", "📊 My claims status"),
    # Add your custom commands
]
```

### Different Storage Backend
The bot uses Google Sheets by default. To use different storage:

1. Modify the services in `services/` folder
2. Update the import statements in handlers
3. Implement your storage interface

### Custom Approval Workflow
Edit `handlers/admin_handlers.py` to modify the approval process:

```python
async def approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add your custom approval logic
    pass
```

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Project Structure
```
├── bot.py                 # Main bot entry point
├── config.py              # Configuration settings
├── models.py              # Data models
├── handlers/              # Command handlers
│   ├── admin_handlers.py
│   ├── user_handlers.py
│   └── ...
├── services/              # External services
│   ├── google_services.py
│   ├── oauth_manager.py
│   └── ...
├── utils/                 # Utility functions
└── data/                  # Data storage
```

## 🔒 Security

- **Never commit sensitive files** (use `.gitignore`)
- **Use environment variables** for production
- **Regularly rotate tokens** and credentials
- **Limit admin privileges** to trusted users only

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram bot token | ✅ |
| `ADMIN_USERNAMES` | Comma-separated admin usernames | ✅ |
| `DRIVE_FOLDER_ID` | Google Drive folder ID | ✅ |
| `SPREADSHEET_NAME` | Name for expense spreadsheet | ❌ |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **"Invalid BOT_TOKEN"**
   - Verify your bot token from @BotFather
   - Check for extra spaces or characters

2. **"Google API Error"**
   - Ensure Google Sheets and Drive APIs are enabled
   - Verify OAuth credentials are correct
   - Check Google Drive folder permissions

3. **"Permission Denied"**
   - Make sure the bot user is in `allowed_users.json`
   - Verify admin usernames are correct

4. **Bot Not Responding**
   - Check internet connection
   - Verify bot token is active
   - Look at `bot.log` for error details

### Getting Help

1. Check the [Issues](../../issues) section
2. Review `bot.log` for error details
3. Run the bot manually to see console output
4. Use the `/auditlog` command to download debug info

## 🎯 Roadmap

- [ ] Multiple language support
- [ ] Database storage option
- [ ] Web dashboard
- [ ] Mobile app integration
- [ ] Advanced reporting
- [ ] Custom approval workflows

---

Made with ❤️ for expense management
