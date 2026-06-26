import os
import datetime
from config import AUDIT_LOG_FILE

def safe_filename(base_name: str, folder: str, ext=".jpg"):
    count = 0
    candidate = f"{base_name}{ext}"
    while os.path.exists(os.path.join(folder, candidate)):
        count += 1
        candidate = f"{base_name}_{count}{ext}"
    return candidate

def get_user_display_name(user):
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return user.first_name
    else:
        return f"user_id_{user.id}"

def format_expense_row(row, index=None):
    idx_str = f"{index}. " if index is not None else ""
    return (f"{idx_str}User: {row[0]}\n"
            f"Date: {row[1]}\n"
            f"Type: {row[2]}\n"
            f"Description: {row[3]}\n"
            f"Amount: {row[4]}\n"
            f"Receipt: {row[5]}")

def audit_log(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} - {message}\n")
            f.flush()  # Ensure data is written immediately
    except Exception as e:
        print(f"Error writing to audit log: {e}")
        # Fallback to console logging if file write fails
        print(f"AUDIT: {timestamp} - {message}")
