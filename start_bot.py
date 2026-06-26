"""
Telegram Bot Launcher - Ensures proper Python path setup
"""
import sys
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the bot directory to Python path
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Now import and run the bot
if __name__ == "__main__":
    try:
        import bot
        # If bot.py has a main function, call it
        if hasattr(bot, 'main'):
            bot.main()
        # Otherwise just importing it should start the bot
    except ImportError as e:
        print(f"❌ Error importing bot: {e}")
        print(f"Current directory: {SCRIPT_DIR}")
        print(f"Python path: {sys.path}")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        input("Press Enter to exit...")
