import json
import os
from .file_lock import safe_file_operation

# Path for storing admin chat IDs
ADMIN_CHAT_FILE = "data/admin_chats.json"

def load_admin_chats():
    """Load admin chat IDs from file. Returns a dict of {username: chat_id}."""
    if os.path.exists(ADMIN_CHAT_FILE):
        try:
            with open(ADMIN_CHAT_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_admin_chats(admin_chats_dict):
    """Save admin chat IDs to file with proper locking."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(ADMIN_CHAT_FILE), exist_ok=True)
    with safe_file_operation(ADMIN_CHAT_FILE):
        with open(ADMIN_CHAT_FILE, "w") as f:
            json.dump(admin_chats_dict, f, indent=2)

def register_admin_chat(username, chat_id):
    """Register an admin's chat ID when they interact with the bot."""
    admin_chats = load_admin_chats()
    admin_chats[username] = chat_id
    save_admin_chats(admin_chats)

def get_admin_chat_ids():
    """Get all admin chat IDs for sending notifications."""
    admin_chats = load_admin_chats()
    return list(admin_chats.values())

def get_admin_chats():
    """Get all admin username -> chat_id mappings."""
    return load_admin_chats()

def remove_admin_chat(username):
    """Remove an admin's chat ID when they are removed as admin. Returns the chat ID if found."""
    admin_chats = load_admin_chats()
    username_lower = username.lower()
    
    # Find and remove the admin chat (case-insensitive)
    removed_chat_id = None
    for admin_username in list(admin_chats.keys()):
        if admin_username.lower() == username_lower:
            removed_chat_id = admin_chats[admin_username]
            del admin_chats[admin_username]
            break
    
    if removed_chat_id:
        save_admin_chats(admin_chats)
        return removed_chat_id
    return None
