from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.auth import is_admin, load_allowed_users, save_allowed_users, is_allowed, get_user_sheet_name
from config import ADMIN_USERNAMES, RECEIPTS_FOLDER, REJECT_REASON
import datetime
import os
from utils.helpers import get_user_display_name, audit_log
from services.google_services import google_services
import logging
from models import PENDING_APPROVAL
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)

# --- Constants ---
CLEANUP_CUTOFF_DAYS = 7

# --- Decorators ---
def admin_required(func: Callable[..., Awaitable[Any]]):
    """Decorator to ensure the user is an admin."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        admin_user = update.message.from_user
        admin_username = admin_user.username or ""
        if not is_admin(admin_username):
            display_name = get_user_display_name(admin_user)
            await update.message.reply_text(f"❌ Sorry {display_name}, only admins can perform this action.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# --- Helpers ---
def get_allowed_users():
    """Load allowed users from file."""
    return load_allowed_users()

def save_users(users):
    """Save allowed users to file."""
    save_allowed_users(users)

def cleanup_receipts(folder: str, cutoff_days: int) -> int:
    """Delete files older than cutoff_days in the given folder. Returns number deleted."""
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=cutoff_days)
    count = 0
    for filename in os.listdir(folder):
        try:
            path = os.path.join(folder, filename)
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            if file_time < cutoff:
                os.remove(path)
                count += 1
        except Exception as e:
            logger.error(f"Error deleting old receipt {filename}: {e}")
    return count

@admin_required
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a user to the allowed list with optional sheet assignment."""
    if not context.args:
        await update.message.reply_text(
            "Usage: /adduser <username> [sheet_name]\n"
            "Examples:\n"
            "• /adduser john_doe (creates sheet 'user_john_doe')\n"
            "• /adduser jane_smith custom_sheet_name\n"
            "• /adduser mike existing_sheet_name"
        )
        return
    
    new_user = context.args[0].lstrip('@')
    sheet_name = context.args[1] if len(context.args) > 1 else f"user_{new_user}"
    
    allowed_users = get_allowed_users()
    if new_user in allowed_users:
        current_sheet = allowed_users[new_user]
        await update.message.reply_text(
            f"User @{new_user} is already allowed.\n"
            f"Current sheet: '{current_sheet}'"
        )
        return
    
    # Check if sheet exists or create it
    all_sheets = google_services.list_all_sheets()
    if sheet_name not in all_sheets:
        await update.message.reply_text(f"Creating new sheet '{sheet_name}'...")
        if google_services.create_user_sheet(sheet_name):
            await update.message.reply_text(f"✅ Sheet '{sheet_name}' created successfully!")
        else:
            await update.message.reply_text(f"❌ Failed to create sheet '{sheet_name}'. Using default.")
            sheet_name = f"user_{new_user}"
    else:
        await update.message.reply_text(f"Using existing sheet '{sheet_name}'")
    
    # Add user with sheet assignment
    allowed_users[new_user] = sheet_name
    save_users(allowed_users)
    
    admin_username = update.message.from_user.username or ""
    audit_log(f"Admin {admin_username} added user @{new_user} with sheet '{sheet_name}'")
    
    await update.message.reply_text(
        f"✅ User @{new_user} added to allowed list.\n"
        f"📄 Assigned to sheet: '{sheet_name}'\n"
        f"🔗 All their expenses will be logged to this sheet."
    )

@admin_required
async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a user from the allowed list with optional sheet deletion."""
    if not context.args:
        await update.message.reply_text(
            "Usage: /removeuser <username> [delete_sheet]\n"
            "Examples:\n"
            "• /removeuser john_doe (keeps sheet)\n"
            "• /removeuser jane_smith delete (deletes sheet)"
        )
        return
    
    rem_user = context.args[0].lstrip('@')
    delete_sheet = len(context.args) > 1 and context.args[1].lower() == 'delete'
    
    allowed_users = get_allowed_users()
    if rem_user not in allowed_users:
        await update.message.reply_text(f"User @{rem_user} is not in allowed list.")
        return
    
    if rem_user in ADMIN_USERNAMES:
        await update.message.reply_text("❌ Cannot remove an admin user.")
        return
    
    # Get user's sheet name before removal
    user_sheet = allowed_users[rem_user]
    
    # Remove user
    del allowed_users[rem_user]
    save_users(allowed_users)
    
    admin_username = update.message.from_user.username or ""
    
    response = f"✅ User @{rem_user} removed from allowed list.\n"
    
    if delete_sheet:
        if google_services.delete_user_sheet(user_sheet):
            response += f"🗑️ Sheet '{user_sheet}' deleted successfully."
            audit_log(f"Admin {admin_username} removed user @{rem_user} and deleted sheet '{user_sheet}'")
        else:
            response += f"❌ Failed to delete sheet '{user_sheet}'. Manual cleanup may be needed."
            audit_log(f"Admin {admin_username} removed user @{rem_user} but failed to delete sheet '{user_sheet}'")
    else:
        response += f"📄 Sheet '{user_sheet}' preserved for historical data."
        audit_log(f"Admin {admin_username} removed user @{rem_user} (sheet '{user_sheet}' preserved)")
    
    await update.message.reply_text(response)

# Admin command to delete an expense entry by row number



async def reject_expense_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_user = update.message.from_user
    admin_username = admin_user.username or ""
    reason = update.message.text.strip()
    expense_id = context.user_data.get("reject_expense_id")
    # Remove debug output
    if not expense_id or expense_id not in PENDING_APPROVAL:
        await update.message.reply_text("❌ No pending expense to reject.")
        return ConversationHandler.END
    expense = PENDING_APPROVAL.pop(expense_id)
    audit_log(f"Admin {admin_username} rejected expense of user {expense['username']} Reason: {reason}")
    reject_msg = f"❌ Rejected by admin @{admin_username}\nReason: {reason}"
    # Edit the original message to remove buttons and show rejection
    try:
        if context.user_data.get("reject_message_id") and context.user_data.get("reject_chat_id"):
            await context.bot.edit_message_caption(
                chat_id=context.user_data["reject_chat_id"],
                message_id=context.user_data["reject_message_id"],
                caption=reject_msg
            )
        else:
            await update.message.reply_text(reject_msg)
    except Exception:
        await update.message.reply_text(reject_msg)
    # Notify user
    try:
        user_msg = f"❌ Your expense submission was rejected by admin.\nReason: {reason}"
        await context.bot.send_message(chat_id=expense["user_id"], text=user_msg)
    except Exception:
        pass
    # Clean up local file after rejection
    try:
        if os.path.exists(expense["img_path"]):
            os.remove(expense["img_path"])
            logger.info(f"Cleaned up local receipt file after rejection: {expense['img_path']}")
    except Exception as e:
        logger.error(f"Failed to clean up local file {expense['img_path']}: {e}")
    return ConversationHandler.END

# Patch approval_callback to store message info for editing
async def approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    admin_user = query.from_user
    admin_username = admin_user.username or ""

    if not is_admin(admin_username):
        # Try to edit caption, fallback to edit text if not possible
        try:
            await query.edit_message_caption("❌ You are not authorized to approve/reject expenses.")
        except Exception:
            await query.edit_message_text("❌ You are not authorized to approve/reject expenses.")
        return

    # Defensive: Only process expected callback data
    if not (data.startswith("approve_") or data.startswith("reject_")):
        await query.edit_message_text("Unknown or invalid action.")
        return
    try:
        action, expense_id = data.split("_", 1)
    except Exception:
        await query.edit_message_text("Invalid callback data format.")
        return
    expense_id = expense_id.split(":", 1)[0]
    if action == "reject":
        context.user_data["reject_expense_id"] = expense_id
        # Store message info for editing later
        context.user_data["reject_message_id"] = query.message.message_id
        context.user_data["reject_chat_id"] = query.message.chat_id
        await query.message.reply_text("Please enter a reason for rejection:")
        return REJECT_REASON
    if expense_id not in PENDING_APPROVAL:
        await query.edit_message_caption("❌ Expense not found or already processed.")
        return
    expense = PENDING_APPROVAL.pop(expense_id)
    if action == "approve":
        try:
            # NOW upload to Google Drive upon approval
            now = datetime.datetime.now()
            month_folder_name = now.strftime("%Y-%m")
            image_url = google_services.upload_to_drive_monthly(expense["img_path"], expense["img_name"], month_folder_name)
            
            # Get user's assigned sheet
            user_sheet = get_user_sheet_name(expense["username"])
            
            # Use the description directly (new format)
            # Convert amount to float to ensure proper number formatting
            amount_value = float(expense["amount"])
            
            google_services.append_to_user_sheet(user_sheet, [
                expense["date"],
                expense["description"],
                amount_value,  # Use numeric value instead of string
                "YES"  # Receipt attached
            ])
            audit_log(f"Admin {admin_username} approved expense of user {expense['username']} to sheet '{user_sheet}'")
            await query.edit_message_caption(
                f"✅ Approved by admin @{admin_username}\n\n"
                f"User: {expense['username']}\n"
                f"Amount: ${expense['amount']:.2f}\n"
                f"Description: {expense['description']}\n"
                f"Sheet: {user_sheet}"
            )
            try:
                await context.bot.send_message(
                    chat_id=expense["user_id"],
                    text=f"✅ Your expense has been approved and recorded to sheet '{user_sheet}'. Thank you!"
                )
            except Exception:
                pass
            
            # Clean up local file after successful approval
            try:
                if os.path.exists(expense["img_path"]):
                    os.remove(expense["img_path"])
                    logger.info(f"Cleaned up local receipt file: {expense['img_path']}")
            except Exception as e:
                logger.error(f"Failed to clean up local file {expense['img_path']}: {e}")
                
        except Exception as e:
            logger.error(f"Error during approval processing: {e}")
            await query.edit_message_caption("❌ Failed to approve expense due to error.")
    return ConversationHandler.END


@admin_required
async def cleanup_old_receipts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean up old receipts and clear all user sheets."""
    display_name = get_user_display_name(update.message.from_user)
    status_message = await update.message.reply_text("🧹 Starting cleanup process...")
    
    # Clean up old receipt files
    count = cleanup_receipts(RECEIPTS_FOLDER, CLEANUP_CUTOFF_DAYS)
    await status_message.edit_text(f"� Cleaned up {count} old receipt(s)...\n🔄 Now clearing sheets...")
    
    # Clear all user sheets
    sheets_cleared = 0
    allowed_users = get_allowed_users()
    
    for username, sheet_name in allowed_users.items():
        if google_services.clear_sheet_data(sheet_name):
            sheets_cleared += 1
            
    await update.message.reply_text(
        f"✅ Cleanup completed!\n"
        f"📂 Removed {count} old receipt(s)\n"
        f"📊 Cleared data from {sheets_cleared} sheet(s)\n"
        f"✨ All sheet formatting preserved"
    )

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = user.username or ""
    display_name = get_user_display_name(user)
    
    # Check if user is authorized to use this bot
    if not is_allowed(username):
        await update.message.reply_text(f"❌ Sorry {display_name}, you are not authorized to use this bot.")
        return
    
    try:
        if is_admin(username):
            status_message = await update.message.reply_text("📊 Calculating expense summaries...")
            # Admin: show all users' summary
            allowed_users = get_allowed_users()
            if not allowed_users:
                await status_message.edit_text(f"Hello {display_name}, no users configured yet.")
                return
            
            msg_lines = [f"💰 Hello {display_name}, here is the claim Summary (Total by User):"]
            total_all = 0
            
            for user_name, sheet_name in allowed_users.items():
                try:
                    sheet_data = google_services.get_user_sheet_data(sheet_name)
                    user_total = 0
                    
                    # All rows from get_user_sheet_data are data rows (8-16)
                    for row in sheet_data:
                        if len(row) >= 3 and row[2].strip():  # Need amount and not empty
                            try:
                                # Clean the amount string and convert to float
                                amt_str = row[2].strip().replace('$', '').replace(',', '')
                                amt = float(amt_str)
                                user_total += amt
                            except (ValueError, IndexError):
                                continue
                    
                    msg_lines.append(f"- {user_name}: ${user_total:.2f}")
                    total_all += user_total
                    
                except Exception as e:
                    logger.error(f"Error reading sheet {sheet_name}: {e}")
                    msg_lines.append(f"- {user_name}: Error reading sheet")
            
            msg_lines.append(f"\n**Total All Users: ${total_all:.2f}**")
            await update.message.reply_text("\n".join(msg_lines))
        else:
            # Normal user: show only their own summary
            user_sheet = get_user_sheet_name(username)
            sheet_data = google_services.get_user_sheet_data(user_sheet)
            
            if not sheet_data:  # Empty sheet
                await update.message.reply_text(f"Hello {display_name}, you have no recorded claims yet.")
                return
            
            total = 0
            # All rows from get_user_sheet_data are data rows (8-16)
            for row in sheet_data:
                if len(row) >= 3 and row[2].strip():  # Need amount and not empty
                    try:
                        # Clean the amount string and convert to float
                        amt_str = row[2].strip().replace('$', '').replace(',', '')
                        amt = float(amt_str)
                        total += amt
                    except (ValueError, IndexError):
                        continue
            
            await update.message.reply_text(f"💰 Hello {display_name}, your total claims: ${total:.2f}")
    except Exception as e:
        logger.error(f"Error in /summary: {e}")
        await update.message.reply_text("❌ Failed to generate summary.")

@admin_required
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all allowed users with their sheet assignments."""
    allowed_users = get_allowed_users()
    admin_username = update.message.from_user.username or ""
    
    if not allowed_users:
        await update.message.reply_text("📋 No users are currently allowed.")
        audit_log(f"Admin {admin_username} listed users (empty list)")
        return
    
    # Separate admins and regular users
    admins = []
    regular_users = []
    
    for user, sheet_name in allowed_users.items():
        if user in ADMIN_USERNAMES:
            admins.append((user, sheet_name))
        else:
            regular_users.append((user, sheet_name))
    
    # Helper to escape MarkdownV2 special chars
    def escape_md(text):
        # Escape MarkdownV2 special characters according to Telegram API docs
        # Must escape: _ * [ ] ( ) ~ ` > # + - = | { } . !
        s = str(text)
        # First escape backslashes
        s = s.replace('\\', '\\\\')
        # Then escape all other special characters
        special_chars = '_*[]()~`>#+-=|{}.!'
        for char in special_chars:
            s = s.replace(char, '\\' + char)
        return s

    # Build response with proper MarkdownV2 formatting
    response_lines = []
    response_lines.append("📋 *Allowed Users & Sheet Assignments:*")
    response_lines.append("")

    if admins:
        response_lines.append("👑 *Admins:*")
        for admin, sheet in sorted(admins):
            escaped_admin = escape_md(admin)
            escaped_sheet = escape_md(sheet)
            response_lines.append(f"• @{escaped_admin} → `{escaped_sheet}`")
        response_lines.append("")

    if regular_users:
        response_lines.append("👤 *Regular Users:*")
        for user, sheet in sorted(regular_users):
            escaped_user = escape_md(user)
            escaped_sheet = escape_md(sheet)
            response_lines.append(f"• @{escaped_user} → `{escaped_sheet}`")
        response_lines.append("")

    response_lines.append(f"*Total:* {len(allowed_users)} user\\(s\\)")
    response_lines.append(f"*Available sheets:* {len(set(allowed_users.values()))} unique sheet\\(s\\)")

    response = "\n".join(response_lines)
    await update.message.reply_text(response, parse_mode='MarkdownV2')
    audit_log(f"Admin {admin_username} listed {len(allowed_users)} users with sheet assignments")

@admin_required
@admin_required
async def list_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all available sheets in the Google Spreadsheet."""
    admin_username = update.message.from_user.username or ""
    
    # Send immediate feedback message
    retrieving_message = await update.message.reply_text("🔄 Retrieving sheets list...")
    
    try:
        all_sheets = google_services.list_all_sheets()
        if not all_sheets:
            await retrieving_message.edit_text("📄 No sheets found in the spreadsheet.")
            return
        
        response = "📄 **Available Sheets:**\n\n"
        for i, sheet_name in enumerate(all_sheets, 1):
            response += f"{i}. `{sheet_name}`\n"
        
        response += f"\n**Total:** {len(all_sheets)} sheet(s)"
        
        await retrieving_message.edit_text(response, parse_mode='Markdown')
        audit_log(f"Admin {admin_username} listed {len(all_sheets)} sheets")
        
    except Exception as e:
        await retrieving_message.edit_text(f"❌ Error listing sheets: {e}")
        audit_log(f"Admin {admin_username} failed to list sheets: {e}")

@admin_required
async def pending_approvals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all pending expense approvals."""
    admin_username = update.message.from_user.username or ""
    
    if not PENDING_APPROVAL:
        await update.message.reply_text("📋 No pending expense approvals.")
        audit_log(f"Admin {admin_username} checked pending approvals (none found)")
        return
    
    response = f"📋 **Pending Expense Approvals ({len(PENDING_APPROVAL)}):**\n\n"
    
    for expense_id, expense in PENDING_APPROVAL.items():
        response += (
            f"🆔 ID: {expense_id[:8]}...\n"
            f"👤 User: {expense['username']}\n"
            f"📅 Date: {expense['date']}\n"
            f"💰 Amount: ${expense['amount']:.2f}\n"
            f"📝 Description: {expense['description']}\n"
            f"📎 Receipt: {expense.get('image_url', 'Available')}\n"
            f"───────────────\n\n"
        )
    
    if len(response) > 4000:  # Telegram message limit
        response = response[:3900] + "...\n\n*Message truncated - too many pending approvals*"
    
    await update.message.reply_text(response)
    audit_log(f"Admin {admin_username} viewed {len(PENDING_APPROVAL)} pending approvals")
