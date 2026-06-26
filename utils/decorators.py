"""Decorators for consistent command access control."""
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from .admin_manager import is_admin
from .helpers import get_user_display_name

def admin_only(func):
    """Decorator to ensure only admins can access a command."""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user:
            await update.message.reply_text("❌ Could not verify user.")
            return
        
        username = update.effective_user.username
        display_name = get_user_display_name(update.effective_user)
        
        if not username or not is_admin(username):
            await update.message.reply_text(
                f"❌ Sorry {display_name}, this command is for admins only."
            )
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapped
