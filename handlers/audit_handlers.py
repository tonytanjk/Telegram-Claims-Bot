from telegram import Update, InputFile
from telegram.ext import ContextTypes
from config import AUDIT_LOG_FILE
import os

async def download_audit_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    from utils.auth import is_admin
    username = user.username or ""
    if not is_admin(username):
        await update.message.reply_text("❌ Only admins can download the audit log.")
        return
    
    status_message = await update.message.reply_text("📂 Retrieving audit log...")
    
    if not os.path.exists(AUDIT_LOG_FILE):
        await status_message.edit_text("📋 No audit log found.")
        return
    
    try:
        with open(AUDIT_LOG_FILE, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename="audit.log"),
                caption="📋 Audit Log File"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error downloading audit log: {str(e)}")
        from utils.helpers import audit_log
        audit_log(f"Error downloading audit log: {e}")
