from asyncio.log import logger
import datetime
import uuid
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import DESCRIPTION, AMOUNT, IMAGE, RECEIPTS_FOLDER
from models import PENDING_APPROVAL, ExpenseData
from utils.auth import is_allowed, get_user_sheet_name
from utils.validators import valid_amount, valid_image_extension
from utils.helpers import get_user_display_name, safe_filename, audit_log
from handlers.admin_handlers import cleanup_old_receipts, summary
from handlers.user_handlers import history, download
from handlers.dashboard_handlers import admin_dashboard
from handlers.audit_handlers import download_audit_log
from services.google_services import google_services

def get_user_and_reply(update, context):
    # Returns (user, reply_func) for both message and callback_query
    if hasattr(update, 'message') and update.message:
        user = update.message.from_user
        reply = update.message.reply_text
    elif hasattr(update, 'callback_query') and update.callback_query:
        user = update.effective_user
        reply = update.callback_query.message.reply_text
    else:
        user = update.effective_user
        reply = lambda text, **kwargs: context.bot.send_message(chat_id=user.id, text=text, **kwargs)
    return user, reply

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, reply = get_user_and_reply(update, context)
    username = user.username or ""
    if not is_allowed(username):
        display_name = get_user_display_name(user)
        await reply(f"❌ Sorry {display_name}, you are not authorized to use this bot.")
        return ConversationHandler.END
    display_name = get_user_display_name(user)
    await reply(
        f"👋 Hello {display_name}! This is strictly for Ignite Claims.\n\n"
        "You can specify date like this:\n"
        "`07/07 Transport` or just `Transport` (defaults to today).\n\n"
        "What is the *Description/Expenses*? (e.g. 07/07 Transport, Food, Fruits, etc.)\n",
        parse_mode='Markdown'
    )
    return DESCRIPTION

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    from utils.auth import is_admin, is_allowed
    from config import ADMIN_COMMANDS
    from telegram import BotCommand, BotCommandScopeChat
    
    username = user.username or ""
    display_name = get_user_display_name(user)
    
    # Check if user is authorized to use this bot
    if not is_allowed(username):
        await update.message.reply_text(
            f"❌ Sorry {display_name}, you are not authorized to use this bot.\n\n"
            "Please contact an administrator to request access."
        )
        return ConversationHandler.END
    
    if is_admin(username):
        # Register admin chat ID for notifications
        from utils.admin_chat_manager import register_admin_chat
        register_admin_chat(username, update.effective_chat.id)
        
        # Set admin commands for this specific chat
        try:
            admin_commands = [BotCommand(command, description) for command, description in ADMIN_COMMANDS]
            await context.bot.set_my_commands(
                admin_commands,
                scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
            )
            logging.getLogger(__name__).info(f"Set admin commands for {username} (chat_id: {update.effective_chat.id})")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to set admin commands for {username}: {e}")
        
        await update.message.reply_text(
            f"👋 Hello {display_name}!\n\n📋 Admin Commands:\n"
            "💼 Expense Management:\n"
            "/claim — Submit a new expense claim (auto-approved)\n"
            "/summary — View total expenses for all users\n"
            "/history — View your last 5 claims\n"
            "/pending — View pending expense approvals\n\n"
            "📊 Reports & Downloads:\n"
            "/download — Download all sheets as Excel (with formatting)\n"
            "/auditlog — Download audit log\n"
            "/dashboard — Access admin dashboard\n\n"
            "👥 User & Admin Management:\n"
            "/listusers — Show all users and their assigned sheets\n"
            "/listsheets — Show all sheets in the system\n"
            "/listadmins — Show all current admins\n"
            "/adduser <username> [sheet_name] — Add user with custom sheet\n"
            "/removeuser <username> [delete] — Remove user access\n"
            "   • Add [delete] to also remove their sheet\n"
            "/addadmin <username> — Add a new admin\n"
            "/removeadmin <username> — Remove an admin\n\n"
            "⚙️ System Tools:\n"
            "/cleanup — Clean up old receipt files and clear sheets\n\n"
            "💡 Tips:\n"
            "• Your claims are auto-approved\n"
            "• Each user has their own sheet\n"
            "• Admin commands have been set in your menu!\n"
            "• Use /pending to check for awaiting approvals"
        )
    else:
        # Set user commands for non-admins (including demoted admins)
        try:
            from config import USER_COMMANDS
            user_commands = [BotCommand(command, description) for command, description in USER_COMMANDS]
            await context.bot.set_my_commands(
                user_commands,
                scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
            )
            logging.getLogger(__name__).info(f"Set user commands for {username} (chat_id: {update.effective_chat.id})")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to set user commands for {username}: {e}")
        
        await update.message.reply_text(
            f"👋 Hello {display_name}!\n\n📋 Available Commands:\n"
            "💼 Expense Management:\n"
            "/claim — Submit a new expense claim (requires admin approval)\n"
            "/history — View your last 5 claims\n"
            "/summary — View your total claims\n\n"
            "⚙️ Other:\n"
            "/cancel — Cancel the current operation\n\n"
            "📝 Claim Process:\n"
            "1. Use /claim to start\n"
            "2. Enter description (e.g., 'Transport', '07/07 Lunch')\n"
            "3. Enter amount (e.g., 12.50)\n"
            "4. Upload receipt photo\n"
            "5. Wait for admin approval\n\n"
            "💡 Tips:\n"
            "• Date format: MM/DD or defaults to today\n"
            "• Receipt photo is required\n"
            "• You'll be notified when approved/rejected\n"
            "• User commands have been set in your menu!"
        )
    return ConversationHandler.END


async def description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, reply = get_user_and_reply(update, context)
    text = None
    if hasattr(update, 'message') and update.message:
        text = update.message.text.strip()
    elif hasattr(update, 'callback_query') and update.callback_query:
        text = update.callback_query.message.text.strip()
    else:
        text = ""
    
    # Parse date from the description if present
    parts = text.split(maxsplit=1)
    date_str = None
    description = text
    
    if len(parts) == 2 and "/" in parts[0]:
        date_str = parts[0]
        description = parts[1]
    
    try:
        if date_str:
            expense_date = datetime.datetime.strptime(date_str, "%m/%d").replace(year=datetime.datetime.now().year)
        else:
            expense_date = datetime.datetime.now()
    except Exception:
        expense_date = datetime.datetime.now()

    context.user_data['date'] = expense_date.strftime("%Y-%m-%d")
    context.user_data['description'] = description
    await reply("How much was the *amount* spent? (e.g. 12.50)", parse_mode='Markdown')
    return AMOUNT

async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, reply = get_user_and_reply(update, context)
    text = None
    if hasattr(update, 'message') and update.message:
        text = update.message.text.strip()
    elif hasattr(update, 'callback_query') and update.callback_query:
        text = update.callback_query.message.text.strip()
    else:
        text = ""
    if not valid_amount(text):
        await reply("❌ Invalid amount format. Please enter a number like 12.50")
        return AMOUNT
    context.user_data['amount'] = text
    await reply("📸 Please send a photo as *proof* (e.g. receipt):", parse_mode='Markdown')
    return IMAGE

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        username = user.username or f"id{user.id}"
        photo = update.message.photo[-1]
        file = await photo.get_file()

        now_str = datetime.datetime.now().strftime("%m%d_%I%M%p")
        base_name = f"{now_str}_{username}_receipt"
        img_name = safe_filename(base_name, RECEIPTS_FOLDER, ".jpg")
        img_path = os.path.join(RECEIPTS_FOLDER, img_name)

        await file.download_to_drive(img_path)

        # Basic file type check
        if not valid_image_extension(img_name):
            await update.message.reply_text("❌ Invalid image type. Only JPG/JPEG/PNG allowed.")
            return IMAGE

        from utils.auth import is_admin
        if is_admin(username):
            # Auto-approve for admins
            # Upload to current month folder on Google Drive
            now = datetime.datetime.now()
            month_folder_name = now.strftime("%Y-%m")
            image_url = google_services.upload_to_drive_monthly(img_path, img_name, month_folder_name)
            
            # Get user's assigned sheet
            user_sheet = get_user_sheet_name(username)
            
            # Use the combined description directly
            # Convert amount to float to ensure proper number formatting
            amount_value = float(context.user_data['amount'])
            
            # Ensure amount is a float and format with 2 decimal places
            google_services.append_to_user_sheet(user_sheet, [
                context.user_data['date'],
                context.user_data['description'],
                float(amount_value),  # Convert to float to ensure proper numeric formatting
                "YES"  # Receipt attached
            ])
            audit_log(f"Admin {username} auto-approved their own expense to sheet '{user_sheet}'.")
            await update.message.reply_text(
                f"✅ Your expense has been auto-approved and recorded to sheet '{user_sheet}'. Thank you!"
            )
            # Optionally, clean up the local file
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception:
                pass
            return ConversationHandler.END
        else:
            # Store info for approval - DON'T upload to Drive yet
            expense_id = str(uuid.uuid4())
            PENDING_APPROVAL[expense_id] = {
                "username": username,
                "date": context.user_data['date'],
                "description": context.user_data['description'],
                "amount": float(context.user_data['amount']),  # Convert to float
                "img_path": img_path,
                "img_name": img_name,
                "user_id": update.message.from_user.id,
                "image_url": None,  # Will be set after approval
            }
            # Prepare approval message and keyboard
            buttons = [
                [
                    InlineKeyboardButton("Approve ✅", callback_data=f"approve_{expense_id}"),
                    InlineKeyboardButton("Reject ❌", callback_data=f"reject_{expense_id}:<reason>")
                ]
            ]
            keyboard = InlineKeyboardMarkup(buttons)
            # Format amount with 2 decimal places and $ symbol
            formatted_amount = "${:.2f}".format(float(context.user_data['amount']))
            msg = (f"🆕 New Expense Submission Pending Approval:\n"
                   f"User: {username}\n"
                   f"Date: {context.user_data['date']}\n"
                   f"Description: {context.user_data['description']}\n"
                   f"Amount: {formatted_amount}\n"
                   f"Receipt: (attached below)")
            # Send approval request to all admins
            from utils.admin_chat_manager import get_admin_chat_ids
            admin_chat_ids = get_admin_chat_ids()
            
            if admin_chat_ids:
                # Send notification to all registered admin chats
                for admin_chat_id in admin_chat_ids:
                    try:
                        with open(img_path, "rb") as img_file:
                            await context.bot.send_photo(
                                chat_id=admin_chat_id,
                                photo=img_file,
                                caption=msg,
                                reply_markup=keyboard
                            )
                        logger.info(f"Sent approval request to admin chat {admin_chat_id}")
                    except Exception as e:
                        logger.error(f"Failed to send approval to admin chat {admin_chat_id}: {e}")
            else:
                logger.warning("No admin chat IDs registered - cannot send approval notifications")
                # Still save the pending approval, admins can check via dashboard
                await update.message.reply_text(
                    "✅ Expense submitted and pending admin approval. "
                    "Note: Admin notifications may not be working - please contact an admin directly."
                )
            
            # Notify the user
            await update.message.reply_text(
                "✅ Expense submitted and pending admin approval. You will be notified once approved."
            )
            audit_log(f"Submission by {username} pending approval.")
            return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error saving image: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again.")
        return IMAGE



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, reply = get_user_and_reply(update, context)
    username = user.username or ""
    display_name = get_user_display_name(user)
    
    # Check if user is authorized to use this bot
    if not is_allowed(username):
        await reply(f"❌ Sorry {display_name}, you are not authorized to use this bot.")
        return ConversationHandler.END
    
    await reply(f"❌ Expense submission cancelled, {display_name}.")
    return ConversationHandler.END
