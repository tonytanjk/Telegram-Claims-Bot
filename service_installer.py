#!/usr/bin/env python3
"""
Windows Service Installer for Telegram Expense Claims Bot
"""

import sys
import os
import win32serviceutil
import win32service
import win32event
import servicemanager
import logging
import threading
import time
from pathlib import Path

class TelegramBotService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TelegramExpenseBot"
    _svc_display_name_ = "Telegram Expense Claims Bot"
    _svc_description_ = "Telegram bot for managing expense claims with Google Sheets integration"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        
        # Setup logging for service
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(
                    os.path.join(os.path.dirname(__file__), 'service.log'),
                    encoding='utf-8'
                )
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
    
    def SvcDoRun(self):
        """Main service execution"""
        try:
            self.logger.info("Starting Telegram Expense Claims Bot Service")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            # Start the bot in a separate thread
            bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            bot_thread.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
            self.logger.info("Service stopped")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, '')
            )
            
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, str(e))
            )
    
    def run_bot(self):
        """Run the telegram bot"""
        try:
            # Change to the script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            os.chdir(script_dir)
            
            # Import and run the bot
            sys.path.insert(0, script_dir)
            
            from bot import main
            main()
            
        except Exception as e:
            self.logger.error(f"Bot execution error: {e}")

def install_service():
    """Install the service"""
    try:
        # Get the path to the current script
        script_path = os.path.abspath(__file__)
        
        # Install the service
        win32serviceutil.InstallService(
            TelegramBotService._svc_reg_class_,
            TelegramBotService._svc_name_,
            TelegramBotService._svc_display_name_,
            description=TelegramBotService._svc_description_,
            startType=win32service.SERVICE_AUTO_START,
            exeName=sys.executable,
            exeArgs=f'"{script_path}"'
        )
        
        print(f"✅ Service '{TelegramBotService._svc_display_name_}' installed successfully!")
        print("💡 You can now start it using: sc start TelegramExpenseBot")
        print("💡 Or use the configurator interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to install service: {e}")
        return False

def uninstall_service():
    """Uninstall the service"""
    try:
        win32serviceutil.RemoveService(TelegramBotService._svc_name_)
        print(f"✅ Service '{TelegramBotService._svc_display_name_}' uninstalled successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to uninstall service: {e}")
        return False

def start_service():
    """Start the service"""
    try:
        win32serviceutil.StartService(TelegramBotService._svc_name_)
        print(f"✅ Service '{TelegramBotService._svc_display_name_}' started successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to start service: {e}")
        return False

def stop_service():
    """Stop the service"""
    try:
        win32serviceutil.StopService(TelegramBotService._svc_name_)
        print(f"✅ Service '{TelegramBotService._svc_display_name_}' stopped successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to stop service: {e}")
        return False

def restart_service():
    """Restart the service"""
    try:
        win32serviceutil.RestartService(TelegramBotService._svc_name_)
        print(f"✅ Service '{TelegramBotService._svc_display_name_}' restarted successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to restart service: {e}")
        return False

def check_service_status():
    """Check service status"""
    try:
        import win32serviceutil
        status = win32serviceutil.QueryServiceStatus(TelegramBotService._svc_name_)
        state = status[1]
        
        states = {
            win32service.SERVICE_STOPPED: "Stopped",
            win32service.SERVICE_START_PENDING: "Starting",
            win32service.SERVICE_STOP_PENDING: "Stopping",
            win32service.SERVICE_RUNNING: "Running",
            win32service.SERVICE_CONTINUE_PENDING: "Continuing",
            win32service.SERVICE_PAUSE_PENDING: "Pausing",
            win32service.SERVICE_PAUSED: "Paused"
        }
        
        state_name = states.get(state, "Unknown")
        print(f"Service Status: {state_name}")
        return state_name
        
    except Exception as e:
        print(f"Service not found or error checking status: {e}")
        return "Not Installed"

def main():
    """Main entry point"""
    if len(sys.argv) == 1:
        # Run as service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TelegramBotService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Handle command line arguments
        command = sys.argv[1].lower()
        
        if command == 'install':
            install_service()
        elif command == 'uninstall':
            uninstall_service()
        elif command == 'start':
            start_service()
        elif command == 'stop':
            stop_service()
        elif command == 'restart':
            restart_service()
        elif command == 'status':
            check_service_status()
        else:
            print("Usage:")
            print("  python service_installer.py install   - Install the service")
            print("  python service_installer.py uninstall - Uninstall the service")
            print("  python service_installer.py start     - Start the service")
            print("  python service_installer.py stop      - Stop the service")
            print("  python service_installer.py restart   - Restart the service")
            print("  python service_installer.py status    - Check service status")

if __name__ == '__main__':
    main()
