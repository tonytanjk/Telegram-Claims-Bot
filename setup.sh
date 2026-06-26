#!/bin/bash

echo "Setting up Telegram Expense Claims Bot..."
echo

# Check if config files exist
if [ ! -f "config.py" ]; then
    echo "Copying example configuration files..."
    cp config_example.py config.py
    echo "✅ Created config.py"
fi

if [ ! -f "oauth_credentials.json" ]; then
    cp oauth_credentials_example.json oauth_credentials.json
    echo "✅ Created oauth_credentials.json"
fi

if [ ! -f "data/admin_users.json" ]; then
    cp data/admin_users_example.json data/admin_users.json
    echo "✅ Created data/admin_users.json"
fi

if [ ! -f "data/allowed_users.json" ]; then
    cp data/allowed_users_example.json data/allowed_users.json
    echo "✅ Created data/allowed_users.json"
fi

echo
echo "⚠️  IMPORTANT: Please edit the following files with your settings:"
echo "   • config.py - Add your bot token, admin usernames, and Google Drive folder ID"
echo "   • oauth_credentials.json - Add your Google OAuth credentials"
echo "   • data/admin_users.json - Add your admin usernames"
echo "   • data/allowed_users.json - Add allowed user list"
echo
echo "📖 See README.md for detailed setup instructions."
echo
