import logging
import sys
import os
import json
from telegram import BotCommandScopeChat
from telegram.ext import ApplicationBuilder, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters, InlineQueryHandler

# Runtime OAuth dependency check for executable
print("🔧 Checking OAuth dependencies...")
try:
    from utils.oauth_runtime_installer import ensure_oauth_modules
    if not ensure_oauth_modules():
        print("❌ Failed to ensure OAuth dependencies")
        input("Press Enter to exit...")
        sys.exit(1)
except Exception as e:
    print(f"⚠️  OAuth dependency check failed: {e}")
    print("Continuing anyway...")

# Add error handling for executable environment
try:
    from config import (
        BOT_TOKEN, DESCRIPTION, AMOUNT, IMAGE, REJECT_REASON,
        ADMIN_USERNAMES, USER_COMMANDS, ADMIN_COMMANDS, validate_config
    )
    
    # Validate configuration early
    if not validate_config():
        input("Press Enter to exit...")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Error importing config: {e}")
    print("Make sure config.py is in the same directory as the executable")
    print("💡 Try running setup.bat to create configuration files")
    input("Press Enter to exit...")
    sys.exit(1)

try:
    from handlers.conversation_handlers import start, claim, description_handler, amount_handler, image_handler, cancel
    from handlers.admin_handlers import add_user, remove_user, approval_callback, cleanup_old_receipts, summary, reject_expense_reason, list_users, list_sheets, pending_approvals
    from handlers.admin_management import add_admin_command, remove_admin_command, list_admins_command
    from handlers.user_handlers import history, download
    from handlers.dashboard_handlers import admin_dashboard
    from handlers.inline_handlers import inline_query
    from handlers.audit_handlers import download_audit_log
except ImportError as e:
    print(f"❌ Error importing handlers: {e}")
    print("Make sure all handler modules are included in the build")
    input("Press Enter to exit...")
    sys.exit(1)

# Setup logging with better formatting for executable
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    format=log_format,
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8') if os.access('.', os.W_OK) else logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def setup_commands(context):
    """Set up bot commands in Telegram menu."""
    from utils.admin_manager import load_admin_users
    from telegram import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
    
    # Default commands for all users
    user_commands = [BotCommand(command, description) for command, description in USER_COMMANDS]
    await context.bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    # Get admin users from admin_users.json
    try:
        admin_users = load_admin_users()
        logger.info(f"Loaded {len(admin_users)} admin users: {admin_users}")
    except Exception as e:
        logger.error(f"Failed to load admin users: {e}")
        admin_users = set()

    # Set up admin commands for each admin
    admin_commands = [BotCommand(command, description) for command, description in ADMIN_COMMANDS]
    for admin_username in admin_users:
        try:
            # First, try to get the admin's chat ID from their username
            admin_chats = await context.bot.get_chat(f"@{admin_username}")
            if admin_chats:
                # Set admin-specific commands for this chat
                await context.bot.set_my_commands(
                    admin_commands,
                    scope=BotCommandScopeChat(chat_id=admin_chats.id)
                )
                logger.info(f"Set admin commands for {admin_username}")
        except Exception as e:
            logger.error(f"Failed to set admin commands for {admin_username}: {e}")
            continue

    logger.info("Bot commands have been set up successfully")

def main():
    """Main function with enhanced error handling"""
    try:
        logger.info("🚀 Starting Telegram Bot...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Initialize automatic token refresh
        logger.info("🔄 Starting automatic token refresh scheduler...")
        from services.oauth_manager import oauth_manager
        from services.token_scheduler import start_token_scheduler
        
        # Start token refresh scheduler (checks every hour)
        start_token_scheduler(oauth_manager, refresh_interval_hours=1)
        logger.info("✅ Token refresh scheduler started")
        
        # Verify bot token
        if not BOT_TOKEN or len(BOT_TOKEN) < 20:
            raise ValueError("Invalid BOT_TOKEN in config.py")
        
        logger.info("Building application...")
        from telegram.ext import JobQueue
        application = ApplicationBuilder().token(BOT_TOKEN).job_queue(JobQueue()).build()

        # Set up bot commands in Telegram menu
        logger.info("Setting up bot commands in Telegram menu...")
        application.job_queue.run_once(setup_commands, 0)

        # Setup conversation handlers
        logger.info("Setting up conversation handlers...")
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("claim", claim)],
            states={
                DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description_handler)],
                AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler)],
                IMAGE: [MessageHandler(filters.PHOTO, image_handler)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )

        admin_approval_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(approval_callback)],
            states={
                REJECT_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, reject_expense_reason)],
            },
            fallbacks=[],
        )

        # Add handlers
        logger.info("Adding command handlers...")
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("summary", summary))
        application.add_handler(CommandHandler("history", history))
        application.add_handler(CommandHandler("download", download))
        application.add_handler(CommandHandler("cleanup", cleanup_old_receipts))
        application.add_handler(CommandHandler("dashboard", admin_dashboard))
        application.add_handler(CommandHandler("auditlog", download_audit_log))
        application.add_handler(CommandHandler("adduser", add_user))
        application.add_handler(CommandHandler("removeuser", remove_user))
        application.add_handler(CommandHandler("listusers", list_users))
        application.add_handler(CommandHandler("listsheets", list_sheets))
        application.add_handler(CommandHandler("addadmin", add_admin_command))
        application.add_handler(CommandHandler("removeadmin", remove_admin_command))
        application.add_handler(CommandHandler("listadmins", list_admins_command))
        application.add_handler(CommandHandler("pending", pending_approvals))

        # Add callback query handler for approval buttons
        application.add_handler(admin_approval_conv, group=1)
        application.add_handler(InlineQueryHandler(inline_query))

        logger.info("✅ Bot setup complete. Starting polling...")
        application.run_polling()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error starting bot: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        print(f"\n❌ Bot failed to start: {e}")
        print(f"Error type: {type(e).__name__}")
        print("\nCommon fixes:")
        print("1. Check if creds.json exists and is valid")
        print("2. Verify BOT_TOKEN in config.py")
        print("3. Ensure data directory exists")
    finally:
        # Clean up token scheduler
        logger.info("🧹 Cleaning up token refresh scheduler...")
        from services.token_scheduler import stop_token_scheduler
        stop_token_scheduler()
        logger.info("✅ Cleanup complete")
        print("4. Check internet connection")
        print("5. Run diagnose-crash.py for detailed analysis")
        
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
