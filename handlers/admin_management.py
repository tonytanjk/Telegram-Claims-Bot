from telegram import Update
from telegram.ext import ContextTypes
from utils.admin_manager import is_admin, add_admin, remove_admin, load_admin_users
from utils.helpers import get_user_display_name, audit_log
from utils.auth import load_allowed_users
import logging

logger = logging.getLogger(__name__)

async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new admin. Only existing admins can add new admins."""
    user = update.message.from_user
    username = user.username or ""
    display_name = get_user_display_name(user)
    
    if not is_admin(username):
        await update.message.reply_text(f"❌ Sorry {display_name}, only admins can add new admins.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /addadmin <username>\n"
            "Example: /addadmin john_doe"
        )
        return
    
    new_admin = context.args[0].lstrip('@').lower()
    
    # Check if username format is valid
    if not new_admin:
        await update.message.reply_text("❌ Invalid username format.")
        return
    
    if add_admin(new_admin):
        audit_log(f"Admin {username} added new admin @{new_admin}")
        await update.message.reply_text(
            f"✅ Successfully added @{new_admin} as an admin.\n\n"
            f"📋 Next steps:\n"
            f"• Ask @{new_admin} to send /start to the bot\n"
            f"• This will register their chat ID for approval notifications\n"
            f"• They will then see admin commands in their menu"
        )
    else:
        await update.message.reply_text(f"❌ @{new_admin} is already an admin.")

async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove an admin. Only admins can remove other admins."""
    user = update.message.from_user
    username = user.username or ""
    display_name = get_user_display_name(user)
    
    if not is_admin(username):
        await update.message.reply_text(f"❌ Sorry {display_name}, only admins can remove admins.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /removeadmin <username>\n"
            "Example: /removeadmin john_doe"
        )
        return
    
    admin_to_remove = context.args[0].lstrip('@').lower()
    
    # Prevent self-removal
    if admin_to_remove.lower() == username.lower():
        await update.message.reply_text("❌ You cannot remove yourself as an admin.")
        return
    
    if remove_admin(admin_to_remove):
        # Also remove their chat ID from admin_chats.json and get the chat ID
        from utils.admin_chat_manager import remove_admin_chat
        from config import USER_COMMANDS
        from telegram import BotCommand, BotCommandScopeChat
        
        removed_chat_id = remove_admin_chat(admin_to_remove)
        
        audit_log(f"Admin {username} removed admin @{admin_to_remove}")
        
        # Update their command menu to user commands if we have their chat ID
        menu_updated = False
        if removed_chat_id:
            try:
                # Set user commands for the demoted admin's chat
                user_commands = [BotCommand(command, description) for command, description in USER_COMMANDS]
                await context.bot.set_my_commands(
                    user_commands,
                    scope=BotCommandScopeChat(chat_id=removed_chat_id)
                )
                menu_updated = True
                print(f"✅ Updated command menu for demoted admin {admin_to_remove}")
            except Exception as e:
                print(f"❌ Failed to update command menu for {admin_to_remove}: {e}")
        
        # Provide feedback based on what was accomplished
        if removed_chat_id and menu_updated:
            await update.message.reply_text(
                f"✅ Successfully removed @{admin_to_remove} as an admin.\n"
                f"📱 Removed from notification list and updated their command menu.\n"
                f"🔄 They now see user commands only."
            )
        elif removed_chat_id:
            await update.message.reply_text(
                f"✅ Successfully removed @{admin_to_remove} as an admin.\n"
                f"📱 Removed from notification list.\n"
                f"⚠️ Could not update their command menu - they may need to restart Telegram."
            )
        else:
            await update.message.reply_text(
                f"✅ Successfully removed @{admin_to_remove} as an admin.\n"
                f"ℹ️ No chat ID was registered for this admin.\n"
                f"💡 Ask them to send /start to see updated commands."
            )
    else:
        current_admins = load_admin_users()
        if len(current_admins) <= 1:
            await update.message.reply_text("❌ Cannot remove the last admin.")
        else:
            await update.message.reply_text(f"❌ @{admin_to_remove} is not an admin.")

async def list_admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all current admins. Only admins can see this."""
    user = update.message.from_user
    username = user.username or ""
    display_name = get_user_display_name(user)
    
    if not is_admin(username):
        await update.message.reply_text(f"❌ Sorry {display_name}, only admins can view the admin list.")
        return
    
    admin_users = load_admin_users()
    if not admin_users:
        await update.message.reply_text("No admins configured.")
        return
    
    msg_lines = ["👥 Current Admins:"]
    for admin in sorted(admin_users):
        msg_lines.append(f"• @{admin}")
    
    await update.message.reply_text("\n".join(msg_lines))
