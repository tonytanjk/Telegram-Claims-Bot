import json
import os
from config import ADMIN_USERNAMES

# Path for storing admin usernames
ADMIN_FILE = "data/admin_users.json"

def load_admin_users():
    """Load admin users from file. Returns a set of admin usernames."""
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "r") as f:
            data = json.load(f)
            return set(data)
    else:
        # Create default structure with initial admins from config
        save_admin_users(ADMIN_USERNAMES)
        return set(ADMIN_USERNAMES)

def save_admin_users(admin_set):
    """Save admin users set to file with proper locking."""
    from .file_lock import safe_file_operation
    # Ensure data directory exists
    os.makedirs(os.path.dirname(ADMIN_FILE), exist_ok=True)
    with safe_file_operation(ADMIN_FILE):
        with open(ADMIN_FILE, "w") as f:
            json.dump(list(admin_set), f, indent=2)

def is_admin(username: str) -> bool:
    """Check if a username is an admin."""
    if not username:
        return False
    admin_users = load_admin_users()
    return username.lower() in {admin.lower() for admin in admin_users}

def add_admin(username: str) -> bool:
    """Add a new admin. Returns True if successful, False if already exists."""
    admin_users = load_admin_users()
    username = username.lower()
    if username in {admin.lower() for admin in admin_users}:
        return False
    admin_users.add(username)
    save_admin_users(admin_users)
    return True

def remove_admin(username: str) -> bool:
    """Remove an admin. Returns True if successful, False if not found or last admin."""
    admin_users = load_admin_users()
    username = username.lower()
    # Prevent removing the last admin
    if len(admin_users) <= 1:
        return False
    # Find the admin (case-insensitive)
    admin_to_remove = None
    for admin in admin_users:
        if admin.lower() == username:
            admin_to_remove = admin
            break
    if admin_to_remove:
        admin_users.remove(admin_to_remove)
        save_admin_users(admin_users)
        return True
    return False
