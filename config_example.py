import os
import json
from typing import Set

# Bot configuration - REQUIRED: Set your bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Folder and file paths
RECEIPTS_FOLDER = "data/receipts"
USER_FILE = "data/allowed_users.json"
AUDIT_LOG_FILE = "data/audit.log"

# Admin configuration - REQUIRED: Set your admin usernames
ADMIN_USERNAMES = set(os.environ.get("ADMIN_USERNAMES", "").split(",")) if os.environ.get("ADMIN_USERNAMES") else {"admin_username"}

# Google Drive configuration - REQUIRED: Set your Google Drive folder ID
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "YOUR_GOOGLE_DRIVE_FOLDER_ID")

# Google API configuration
GOOGLE_SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Spreadsheet configuration - OPTIONAL: Customize your spreadsheet name
SPREADSHEET_NAME = os.environ.get("SPREADSHEET_NAME", "EXPENSE_CLAIMS")

# Conversation states
DESCRIPTION, AMOUNT, IMAGE, REJECT_REASON = range(4)

# Create necessary directories
os.makedirs(RECEIPTS_FOLDER, exist_ok=True)

# Bot command descriptions - CUSTOMIZABLE: Modify these as needed
USER_COMMANDS = [
    ("claim", "📝 Submit a new expense claim"),
    ("summary", "💰 View your total claims"),
    ("history", "📋 View your last 5 claims"),
    ("cancel", "❌ Cancel current operation"),
]

ADMIN_COMMANDS = [
    ("claim", "📝 Submit a new expense claim (auto-approved)"),
    ("summary", "💰 View total expenses by user"),
    ("history", "📋 View your last 5 claims"),
    ("download", "📥 Download all expense sheets as Excel"),
    ("auditlog", "📊 Download audit log"),
    ("pending", "⏳ View pending expense approvals"),
    ("adduser", "➕ Add a new user"),
    ("removeuser", "➖ Remove a user"),
    ("addadmin", "👑 Add a new admin"),
    ("removeadmin", "👑 Remove an admin"),
    ("listusers", "👥 List all users"),
    ("listsheets", "📑 List all sheets"),
    ("listadmins", "👑 List all admins"),
    ("cleanup", "🧹 Clean up old files and sheets"),
    ("dashboard", "📊 Access admin dashboard"),
]

# Validation
def validate_config():
    """Validate that required configuration is set"""
    errors = []
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        errors.append("BOT_TOKEN is not set. Please set your Telegram bot token.")
    
    if not DRIVE_FOLDER_ID or DRIVE_FOLDER_ID == "YOUR_GOOGLE_DRIVE_FOLDER_ID":
        errors.append("DRIVE_FOLDER_ID is not set. Please set your Google Drive folder ID.")
    
    if ADMIN_USERNAMES == {"admin_username"}:
        errors.append("ADMIN_USERNAMES contains default value. Please set your admin usernames.")
    
    if errors:
        print("❌ Configuration Error:")
        for error in errors:
            print(f"   • {error}")
        print("\n📖 Please see README.md for setup instructions.")
        return False
    
    return True

# Auto-validate on import (for early error detection)
if __name__ != "__main__":
    if not validate_config():
        import sys
        sys.exit(1)
