# Telegram Expense Claims Bot 🤖💰

A comprehensive Telegram bot for managing expense claims with Google Sheets integration and Windows service support.

## ✨ Features

- 📱 **Telegram Integration**: Submit expense claims directly through Telegram
- 📊 **Google Sheets**: Automatic data sync to Google Sheets
- 👥 **User Management**: Admin and user role management
- 🔐 **OAuth Authentication**: Secure Google API integration
- 🖥️ **Windows Service**: Run as a background service
- 🎛️ **GUI Configurator**: Easy setup and configuration interface
- 📝 **Audit Logging**: Track all bot activities
- 🔄 **Auto Token Refresh**: Automatic OAuth token management

## 🚀 Quick Start

### Method 1: Setup Wizard (Recommended)
1. Download or clone this repository
2. Run `setup_wizard.bat` as Administrator
3. Follow the interactive setup process
4. Use the GUI configurator for easy configuration

### Method 2: Manual Setup
1. Install Python 3.8+ from [python.org](https://python.org)
2. Install required packages:
   ```bash
   pip install python-telegram-bot google-api-python-client google-auth-httplib2 google-auth-oauthlib pywin32
   ```
3. Copy example files:
   ```bash
   copy config_example.py config.py
   copy oauth_credentials_example.json oauth_credentials.json
   ```
4. Edit configuration files with your settings
5. Run the bot: `python bot.py`

## 🎛️ Configuration Interface

Launch the GUI configurator for easy setup:
```bash
python configurator.py
```

The configurator provides:
- **Bot Configuration**: Set bot token, name, and basic settings
- **Google Integration**: Configure OAuth and Google Sheets
- **User Management**: Manage admins and allowed users
- **Service Control**: Install, start, stop Windows service
- **Logs & Monitoring**: View real-time logs and status

## 🔧 Configuration Files

### config.py
Main bot configuration:
```python
BOT_TOKEN = "your_bot_token_here"
BOT_NAME = "Expense Claims Bot"
DRIVE_FOLDER_ID = "your_google_drive_folder_id"
SHEET_TYPE = "expense_tracker"  # or "receipt_log", "financial_report", "custom"
DEFAULT_CURRENCY = "USD"
TIMEZONE = "UTC"
```

### oauth_credentials.json
Google OAuth 2.0 credentials:
```json
{
  "installed": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

### data/admin_users.json
List of admin usernames:
```json
["admin_username1", "admin_username2"]
```

### data/allowed_users.json
List of allowed user usernames:
```json
["user1", "user2", "user3"]
```

## 🤖 Getting a Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the bot token provided
5. Add the token to your `config.py` file

## 🔗 Google Sheets Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create OAuth 2.0 credentials (Desktop Application)
5. Download the credentials file as `oauth_credentials.json`
6. Create a Google Drive folder and copy its ID
7. Add the folder ID to your `config.py`

## 🖥️ Windows Service Installation

### Using GUI Configurator
1. Open configurator: `python configurator.py`
2. Go to "Service Control" tab
3. Click "Install as Windows Service"
4. Use Start/Stop buttons to control the service

### Using Command Line
```bash
# Install service
python service_installer.py install

# Start service
python service_installer.py start

# Stop service
python service_installer.py stop

# Check status
python service_installer.py status

# Uninstall service
python service_installer.py uninstall
```

## 📱 Bot Commands

### User Commands
- `/start` - Start the bot and see available commands
- `/claim` - Submit a new expense claim
- `/history` - View your expense history
- `/cancel` - Cancel current operation

### Admin Commands
- `/summary` - View expense summary
- `/download` - Download expense data
- `/dashboard` - Admin dashboard
- `/adduser` - Add allowed user
- `/removeuser` - Remove allowed user
- `/listusers` - List allowed users
- `/addadmin` - Add admin user
- `/removeadmin` - Remove admin user
- `/listadmins` - List admin users
- `/pending` - View pending approvals
- `/cleanup` - Cleanup old receipts
- `/auditlog` - Download audit log

## 📋 Sheet Types

### Expense Tracker (Default)
Basic expense tracking with categories and approval workflow.

### Receipt Log
Detailed receipt logging with image storage and metadata.

### Financial Report
Comprehensive financial reporting with analytics.

### Custom
Define your own sheet structure and fields.

## 🔧 Environment Variables

You can override configuration using environment variables:
- `TELEGRAM_BOT_TOKEN` - Override bot token
- `GOOGLE_DRIVE_FOLDER_ID` - Override Google Drive folder
- `BOT_ENV` - Set to "production" for production mode

## 📊 Monitoring & Logs

### Log Files
- `bot.log` - Main bot activity log
- `service.log` - Windows service log (when running as service)
- `data/audit.log` - User activity audit log

### GUI Monitoring
Use the configurator's "Logs & Status" tab to:
- View real-time logs
- Monitor service status
- Export logs for analysis

## 🔒 Security Features

- **OAuth 2.0**: Secure Google API authentication
- **User Whitelisting**: Control who can use the bot
- **Admin Roles**: Separate admin and user permissions
- **Audit Logging**: Track all user activities
- **Token Encryption**: Secure token storage
- **Auto Refresh**: Automatic token renewal

## 🛠️ Troubleshooting

### Common Issues

**Bot not responding:**
- Check bot token is correct
- Verify bot is running
- Check internet connection

**Google Sheets not working:**
- Verify OAuth credentials
- Check Google Drive folder permissions
- Ensure APIs are enabled

**Service won't start:**
- Run as Administrator
- Check service logs
- Verify configuration files

**Permission denied:**
- Run setup as Administrator
- Check file permissions
- Verify user has service install rights

### Getting Help

1. Check the logs in the configurator
2. Verify all configuration files are correct
3. Test the bot manually before installing as service
4. Check Windows Event Viewer for service errors

## 📁 Project Structure

```
telegram_bot_portable_final/
├── bot.py                      # Main bot entry point
├── configurator.py             # GUI configuration tool
├── service_installer.py        # Windows service installer
├── setup_wizard.bat           # Interactive setup script
├── config.py                  # Bot configuration
├── config_example.py          # Configuration template
├── oauth_credentials.json     # Google OAuth credentials
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                 # Git ignore rules
├── data/                      # Data storage
│   ├── admin_users.json      # Admin users list
│   ├── allowed_users.json    # Allowed users list
│   ├── audit.log             # Audit log
│   └── receipts/             # Receipt images
├── handlers/                  # Bot message handlers
│   ├── admin_handlers.py     # Admin commands
│   ├── user_handlers.py      # User commands
│   ├── conversation_handlers.py # Multi-step conversations
│   └── ...
├── services/                  # Background services
│   ├── oauth_manager.py      # OAuth management
│   ├── token_scheduler.py    # Token refresh scheduler
│   └── ...
└── utils/                     # Utility functions
    ├── admin_manager.py      # Admin management
    ├── auth.py               # Authentication
    └── ...
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [Google APIs](https://developers.google.com/sheets/api) - Google Sheets integration
- [PyWin32](https://github.com/mhammond/pywin32) - Windows service support

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
