import json
import os
from config import USER_FILE, ADMIN_USERNAMES

def load_allowed_users():
    """Load allowed users from file. Returns dict with username -> sheet_name mapping."""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            data = json.load(f)
            # Handle legacy format (list) - convert to dict
            if isinstance(data, list):
                user_dict = {}
                for user in data:
                    user_dict[user] = f"user_{user}"  # Default sheet name
                save_allowed_users(user_dict)
                return user_dict
            return data
    else:
        # Create default structure for admins
        default = {}
        for admin in ADMIN_USERNAMES:
            default[admin] = f"user_{admin}"
        save_allowed_users(default)
        return default

def save_allowed_users(users_dict):
    """Save allowed users dict to file."""
    with open(USER_FILE, "w") as f:
        json.dump(users_dict, f, indent=2)

def get_user_sheet_name(username: str) -> str:
    """Get the sheet name assigned to a user."""
    users = load_allowed_users()
    return users.get(username, f"user_{username}")

def is_admin(username: str) -> bool:
    """Check if a user is an admin using the admin_manager."""
    from .admin_manager import load_admin_users
    admin_users = load_admin_users()
    return username.lower() in {admin.lower() for admin in admin_users}

def is_allowed(username: str) -> bool:
    allowed_users = load_allowed_users()
    return username in allowed_users or is_admin(username)
