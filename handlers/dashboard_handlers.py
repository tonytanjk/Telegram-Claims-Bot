import os
from telegram import Update
from telegram.ext import ContextTypes
from models import PENDING_APPROVAL
from utils.auth import is_admin
from utils.helpers import audit_log

async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = user.username or ""
    if not is_admin(username):
        await update.message.reply_text("❌ Only admins can use this command.")
        return
    
    # Pending approvals
    pending_count = len(PENDING_APPROVAL)
    
    # Recent activity: last 10 audit log lines
    try:
        if os.path.exists("audit.log"):
            with open("audit.log", "r", encoding="utf-8") as f:
                lines = f.readlines()[-10:]
        else:
            lines = []
    except Exception as e:
        lines = []
        audit_log(f"Error reading audit log in dashboard: {e}")
    
    recent_activity = "\n".join(line.strip() for line in lines) if lines else "No recent activity."
    
    msg = (f"📊 Admin Dashboard\n\n"
           f"Pending approvals: {pending_count}\n\n"
           f"Recent activity (last 10):\n{recent_activity}")
    
    await update.message.reply_text(msg)
