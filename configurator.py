#!/usr/bin/env python3
"""
Telegram Bot Configurator
Interactive configuration tool for the Telegram Expense Claims Bot
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import threading
import webbrowser
from pathlib import Path

class BotConfigurator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Telegram Expense Claims Bot - Configurator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Configuration data
        self.config_data = {}
        self.oauth_data = {}
        self.admin_users = []
        self.allowed_users = []
        
        # Service status
        self.service_running = False
        
        self.create_widgets()
        self.load_existing_config()
        self.check_service_status()
        
    def create_widgets(self):
        """Create the main interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_bot_config_tab()
        self.create_google_config_tab()
        self.create_users_tab()
        self.create_service_tab()
        self.create_logs_tab()
        
        # Status bar
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side='left')
        
        # Service status indicator
        self.service_status_label = ttk.Label(self.status_frame, text="Service: Stopped")
        self.service_status_label.pack(side='right')
        
    def create_bot_config_tab(self):
        """Bot Configuration Tab"""
        bot_frame = ttk.Frame(self.notebook)
        self.notebook.add(bot_frame, text="Bot Configuration")
        
        # Bot Token Section
        ttk.Label(bot_frame, text="Bot Token Configuration", font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        token_frame = ttk.Frame(bot_frame)
        token_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(token_frame, text="Bot Token:").pack(anchor='w')
        self.bot_token_var = tk.StringVar()
        self.bot_token_entry = ttk.Entry(token_frame, textvariable=self.bot_token_var, show="*", width=60)
        self.bot_token_entry.pack(fill='x', pady=2)
        
        ttk.Button(token_frame, text="Get Bot Token Help", 
                  command=self.open_bot_token_help).pack(pady=5)
        
        # Bot Settings Section
        ttk.Label(bot_frame, text="Bot Settings", font=('Arial', 12, 'bold')).pack(pady=(20, 5))
        
        settings_frame = ttk.Frame(bot_frame)
        settings_frame.pack(fill='x', padx=20, pady=5)
        
        # Bot Name
        ttk.Label(settings_frame, text="Bot Name:").pack(anchor='w')
        self.bot_name_var = tk.StringVar(value="Expense Claims Bot")
        ttk.Entry(settings_frame, textvariable=self.bot_name_var, width=40).pack(anchor='w', pady=2)
        
        # Expense Settings
        ttk.Label(settings_frame, text="Default Currency:").pack(anchor='w', pady=(10, 0))
        self.currency_var = tk.StringVar(value="USD")
        currency_combo = ttk.Combobox(settings_frame, textvariable=self.currency_var, 
                                     values=["USD", "EUR", "GBP", "SGD", "MYR", "THB"], width=10)
        currency_combo.pack(anchor='w', pady=2)
        
        # Timezone
        ttk.Label(settings_frame, text="Timezone:").pack(anchor='w', pady=(10, 0))
        self.timezone_var = tk.StringVar(value="UTC")
        timezone_combo = ttk.Combobox(settings_frame, textvariable=self.timezone_var,
                                     values=["UTC", "Asia/Singapore", "Asia/Kuala_Lumpur", 
                                            "America/New_York", "Europe/London"], width=20)
        timezone_combo.pack(anchor='w', pady=2)
        
    def create_google_config_tab(self):
        """Google Integration Tab"""
        google_frame = ttk.Frame(self.notebook)
        self.notebook.add(google_frame, text="Google Integration")
        
        # Instructions
        instruction_text = """
        To use Google Sheets integration, you need to:
        1. Create a Google Cloud Project
        2. Enable Google Sheets and Drive APIs
        3. Create OAuth 2.0 credentials
        4. Download the credentials file
        """
        
        ttk.Label(google_frame, text="Google Sheets Configuration", 
                 font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        ttk.Label(google_frame, text=instruction_text, justify='left').pack(pady=10, padx=20)
        
        # OAuth Credentials
        oauth_frame = ttk.Frame(google_frame)
        oauth_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(oauth_frame, text="Setup Google OAuth (Opens Browser)", 
                  command=self.setup_google_oauth).pack(pady=5)
        
        ttk.Button(oauth_frame, text="Upload OAuth Credentials File", 
                  command=self.upload_oauth_file).pack(pady=5)
        
        self.oauth_status_label = ttk.Label(oauth_frame, text="OAuth Status: Not Configured")
        self.oauth_status_label.pack(pady=5)
        
        # Sheet Configuration
        sheet_frame = ttk.Frame(google_frame)
        sheet_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(sheet_frame, text="Google Drive Folder ID:").pack(anchor='w')
        self.drive_folder_var = tk.StringVar()
        ttk.Entry(sheet_frame, textvariable=self.drive_folder_var, width=60).pack(fill='x', pady=2)
        
        ttk.Label(sheet_frame, text="Sheet Template Type:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        
        self.sheet_type_var = tk.StringVar(value="expense_tracker")
        sheet_types = [
            ("Expense Tracker", "expense_tracker"),
            ("Receipt Log", "receipt_log"),
            ("Financial Report", "financial_report"),
            ("Custom", "custom")
        ]
        
        for text, value in sheet_types:
            ttk.Radiobutton(sheet_frame, text=text, variable=self.sheet_type_var, 
                           value=value).pack(anchor='w')
        
    def create_users_tab(self):
        """Users Management Tab"""
        users_frame = ttk.Frame(self.notebook)
        self.notebook.add(users_frame, text="Users & Admins")
        
        # Admin Users Section
        ttk.Label(users_frame, text="Admin Users", font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        admin_frame = ttk.Frame(users_frame)
        admin_frame.pack(fill='both', expand=True, padx=20, pady=5)
        
        admin_input_frame = ttk.Frame(admin_frame)
        admin_input_frame.pack(fill='x', pady=5)
        
        ttk.Label(admin_input_frame, text="Add Admin Username:").pack(side='left')
        self.admin_username_var = tk.StringVar()
        admin_entry = ttk.Entry(admin_input_frame, textvariable=self.admin_username_var)
        admin_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(admin_input_frame, text="Add", 
                  command=self.add_admin_user).pack(side='right')
        
        # Admin listbox
        self.admin_listbox = tk.Listbox(admin_frame, height=6)
        self.admin_listbox.pack(fill='both', expand=True, pady=5)
        
        admin_buttons_frame = ttk.Frame(admin_frame)
        admin_buttons_frame.pack(fill='x')
        
        ttk.Button(admin_buttons_frame, text="Remove Selected", 
                  command=self.remove_admin_user).pack(side='left')
        
        # Allowed Users Section
        ttk.Label(users_frame, text="Allowed Users", font=('Arial', 12, 'bold')).pack(pady=(20, 5))
        
        users_input_frame = ttk.Frame(users_frame)
        users_input_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(users_input_frame, text="Add Username:").pack(side='left')
        self.user_username_var = tk.StringVar()
        user_entry = ttk.Entry(users_input_frame, textvariable=self.user_username_var)
        user_entry.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(users_input_frame, text="Add", 
                  command=self.add_allowed_user).pack(side='right')
        
        # Users listbox
        users_list_frame = ttk.Frame(users_frame)
        users_list_frame.pack(fill='both', expand=True, padx=20, pady=5)
        
        self.users_listbox = tk.Listbox(users_list_frame, height=6)
        self.users_listbox.pack(fill='both', expand=True, pady=5)
        
        users_buttons_frame = ttk.Frame(users_list_frame)
        users_buttons_frame.pack(fill='x')
        
        ttk.Button(users_buttons_frame, text="Remove Selected", 
                  command=self.remove_allowed_user).pack(side='left')
        ttk.Button(users_buttons_frame, text="Allow All Users", 
                  command=self.toggle_allow_all).pack(side='right')
        
    def create_service_tab(self):
        """Service Management Tab"""
        service_frame = ttk.Frame(self.notebook)
        self.notebook.add(service_frame, text="Service Control")
        
        ttk.Label(service_frame, text="Service Management", 
                 font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        # Service status
        status_frame = ttk.Frame(service_frame)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.service_status_detail = ttk.Label(status_frame, text="Service Status: Checking...")
        self.service_status_detail.pack()
        
        # Service controls
        controls_frame = ttk.Frame(service_frame)
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(controls_frame, text="Install as Windows Service", 
                  command=self.install_service).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Start Service", 
                  command=self.start_service).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Stop Service", 
                  command=self.stop_service).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Restart Service", 
                  command=self.restart_service).pack(side='left', padx=5)
        
        # Manual controls
        manual_frame = ttk.Frame(service_frame)
        manual_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(manual_frame, text="Manual Controls", 
                 font=('Arial', 11, 'bold')).pack(anchor='w')
        
        manual_buttons_frame = ttk.Frame(manual_frame)
        manual_buttons_frame.pack(fill='x', pady=5)
        
        ttk.Button(manual_buttons_frame, text="Test Bot (Run Once)", 
                  command=self.test_bot).pack(side='left', padx=5)
        ttk.Button(manual_buttons_frame, text="Save Configuration", 
                  command=self.save_configuration).pack(side='left', padx=5)
        ttk.Button(manual_buttons_frame, text="Reset to Defaults", 
                  command=self.reset_configuration).pack(side='right', padx=5)
        
    def create_logs_tab(self):
        """Logs Tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs & Status")
        
        ttk.Label(logs_frame, text="Bot Logs", font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=20, width=80)
        self.log_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Log controls
        log_controls_frame = ttk.Frame(logs_frame)
        log_controls_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Button(log_controls_frame, text="Refresh Logs", 
                  command=self.refresh_logs).pack(side='left', padx=5)
        ttk.Button(log_controls_frame, text="Clear Logs", 
                  command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(log_controls_frame, text="Export Logs", 
                  command=self.export_logs).pack(side='right', padx=5)
        
    def load_existing_config(self):
        """Load existing configuration files"""
        try:
            # Load config.py
            if os.path.exists('config.py'):
                with open('config.py', 'r') as f:
                    content = f.read()
                    # Parse basic values (simplified parsing)
                    if 'BOT_TOKEN' in content:
                        token_line = [line for line in content.split('\n') if 'BOT_TOKEN' in line and '=' in line]
                        if token_line:
                            token = token_line[0].split('=')[1].strip().strip('"\'')
                            self.bot_token_var.set(token)
            
            # Load OAuth credentials
            if os.path.exists('oauth_credentials.json'):
                with open('oauth_credentials.json', 'r') as f:
                    self.oauth_data = json.load(f)
                    self.oauth_status_label.config(text="OAuth Status: Configured ✓")
            
            # Load admin users
            if os.path.exists('data/admin_users.json'):
                with open('data/admin_users.json', 'r') as f:
                    self.admin_users = json.load(f)
                    for admin in self.admin_users:
                        self.admin_listbox.insert(tk.END, admin)
            
            # Load allowed users
            if os.path.exists('data/allowed_users.json'):
                with open('data/allowed_users.json', 'r') as f:
                    self.allowed_users = json.load(f)
                    for user in self.allowed_users:
                        self.users_listbox.insert(tk.END, user)
                        
        except Exception as e:
            self.update_status(f"Error loading config: {e}")
    
    def save_configuration(self):
        """Save all configuration"""
        try:
            # Validate required fields
            if not self.bot_token_var.get():
                messagebox.showerror("Error", "Bot Token is required!")
                return
            
            # Save config.py
            config_content = f'''# Telegram Bot Configuration
import os
from typing import List, Tuple

# Bot Configuration
BOT_TOKEN = "{self.bot_token_var.get()}"
BOT_NAME = "{self.bot_name_var.get()}"

# Google Drive Configuration
DRIVE_FOLDER_ID = "{self.drive_folder_var.get()}"
SHEET_TYPE = "{self.sheet_type_var.get()}"

# Bot Settings
DEFAULT_CURRENCY = "{self.currency_var.get()}"
TIMEZONE = "{self.timezone_var.get()}"

# Conversation States
DESCRIPTION, AMOUNT, IMAGE, REJECT_REASON = range(4)

# User Commands (visible to all users)
USER_COMMANDS: List[Tuple[str, str]] = [
    ("start", "Start the bot and see available commands"),
    ("claim", "Submit a new expense claim"),
    ("history", "View your expense history"),
    ("cancel", "Cancel current operation"),
]

# Admin Commands (visible to admins only)
ADMIN_COMMANDS: List[Tuple[str, str]] = [
    ("summary", "View expense summary"),
    ("download", "Download expense data"),
    ("dashboard", "Admin dashboard"),
    ("adduser", "Add allowed user"),
    ("removeuser", "Remove allowed user"),
    ("listusers", "List allowed users"),
    ("addadmin", "Add admin user"),
    ("removeadmin", "Remove admin user"),
    ("listadmins", "List admin users"),
    ("pending", "View pending approvals"),
    ("cleanup", "Cleanup old receipts"),
    ("auditlog", "Download audit log"),
]

def validate_config() -> bool:
    """Validate the configuration"""
    if not BOT_TOKEN or len(BOT_TOKEN) < 20:
        print("❌ Invalid BOT_TOKEN. Please check your configuration.")
        return False
    
    if not DRIVE_FOLDER_ID:
        print("⚠️  DRIVE_FOLDER_ID not set. Google Sheets integration will not work.")
    
    return True

# Environment-based overrides
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', BOT_TOKEN)
DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID', DRIVE_FOLDER_ID)
'''
            
            with open('config.py', 'w') as f:
                f.write(config_content)
            
            # Save admin users
            os.makedirs('data', exist_ok=True)
            with open('data/admin_users.json', 'w') as f:
                json.dump(self.admin_users, f, indent=2)
            
            # Save allowed users
            with open('data/allowed_users.json', 'w') as f:
                json.dump(self.allowed_users, f, indent=2)
            
            self.update_status("Configuration saved successfully!")
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            error_msg = f"Error saving configuration: {e}"
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def add_admin_user(self):
        """Add admin user"""
        username = self.admin_username_var.get().strip()
        if username and username not in self.admin_users:
            self.admin_users.append(username)
            self.admin_listbox.insert(tk.END, username)
            self.admin_username_var.set("")
    
    def remove_admin_user(self):
        """Remove selected admin user"""
        selection = self.admin_listbox.curselection()
        if selection:
            index = selection[0]
            username = self.admin_listbox.get(index)
            self.admin_users.remove(username)
            self.admin_listbox.delete(index)
    
    def add_allowed_user(self):
        """Add allowed user"""
        username = self.user_username_var.get().strip()
        if username and username not in self.allowed_users:
            self.allowed_users.append(username)
            self.users_listbox.insert(tk.END, username)
            self.user_username_var.set("")
    
    def remove_allowed_user(self):
        """Remove selected allowed user"""
        selection = self.users_listbox.curselection()
        if selection:
            index = selection[0]
            username = self.users_listbox.get(index)
            self.allowed_users.remove(username)
            self.users_listbox.delete(index)
    
    def toggle_allow_all(self):
        """Toggle allow all users setting"""
        # This would modify the configuration to allow all users
        pass
    
    def open_bot_token_help(self):
        """Open BotFather help in browser"""
        webbrowser.open("https://core.telegram.org/bots#6-botfather")
    
    def setup_google_oauth(self):
        """Open Google OAuth setup guide"""
        webbrowser.open("https://developers.google.com/sheets/api/quickstart/python")
    
    def upload_oauth_file(self):
        """Upload OAuth credentials file"""
        file_path = filedialog.askopenfilename(
            title="Select OAuth Credentials File",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                import shutil
                shutil.copy(file_path, 'oauth_credentials.json')
                self.oauth_status_label.config(text="OAuth Status: Configured ✓")
                self.update_status("OAuth credentials uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload OAuth file: {e}")
    
    def check_service_status(self):
        """Check if service is running"""
        try:
            # Check if service is installed and running
            result = subprocess.run(['sc', 'query', 'TelegramExpenseBot'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                if 'RUNNING' in result.stdout:
                    self.service_running = True
                    self.service_status_label.config(text="Service: Running ✓")
                    self.service_status_detail.config(text="Service Status: Running ✓")
                else:
                    self.service_status_label.config(text="Service: Stopped")
                    self.service_status_detail.config(text="Service Status: Installed but Stopped")
            else:
                self.service_status_label.config(text="Service: Not Installed")
                self.service_status_detail.config(text="Service Status: Not Installed")
        except Exception:
            self.service_status_label.config(text="Service: Unknown")
            self.service_status_detail.config(text="Service Status: Unable to Check")
    
    def install_service(self):
        """Install bot as Windows service"""
        try:
            # Run service installer
            subprocess.run([sys.executable, 'service_installer.py', 'install'], 
                          check=True)
            self.update_status("Service installed successfully!")
            messagebox.showinfo("Success", "Service installed successfully!")
            self.check_service_status()
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install service: {e}"
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def start_service(self):
        """Start the service"""
        try:
            subprocess.run(['sc', 'start', 'TelegramExpenseBot'], check=True)
            self.update_status("Service started!")
            self.check_service_status()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to start service: {e}")
    
    def stop_service(self):
        """Stop the service"""
        try:
            subprocess.run(['sc', 'stop', 'TelegramExpenseBot'], check=True)
            self.update_status("Service stopped!")
            self.check_service_status()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to stop service: {e}")
    
    def restart_service(self):
        """Restart the service"""
        self.stop_service()
        threading.Timer(2.0, self.start_service).start()
    
    def test_bot(self):
        """Test run the bot"""
        def run_test():
            try:
                self.update_status("Testing bot... (Check console for output)")
                result = subprocess.run([sys.executable, 'bot.py', '--test'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    self.update_status("Bot test completed successfully!")
                else:
                    self.update_status(f"Bot test failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                self.update_status("Bot test timed out (this may be normal)")
            except Exception as e:
                self.update_status(f"Bot test error: {e}")
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def reset_configuration(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all configuration?"):
            # Clear all fields
            self.bot_token_var.set("")
            self.bot_name_var.set("Expense Claims Bot")
            self.currency_var.set("USD")
            self.timezone_var.set("UTC")
            self.drive_folder_var.set("")
            self.sheet_type_var.set("expense_tracker")
            
            # Clear lists
            self.admin_listbox.delete(0, tk.END)
            self.users_listbox.delete(0, tk.END)
            self.admin_users.clear()
            self.allowed_users.clear()
            
            self.update_status("Configuration reset to defaults")
    
    def refresh_logs(self):
        """Refresh log display"""
        try:
            if os.path.exists('bot.log'):
                with open('bot.log', 'r', encoding='utf-8') as f:
                    logs = f.read()
                    self.log_text.delete(1.0, tk.END)
                    self.log_text.insert(tk.END, logs)
                    self.log_text.see(tk.END)
            else:
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, "No log file found.")
        except Exception as e:
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, f"Error reading logs: {e}")
    
    def clear_logs(self):
        """Clear log file"""
        try:
            if os.path.exists('bot.log'):
                os.remove('bot.log')
                self.log_text.delete(1.0, tk.END)
                self.update_status("Logs cleared")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear logs: {e}")
    
    def export_logs(self):
        """Export logs to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Logs",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                import shutil
                shutil.copy('bot.log', file_path)
                self.update_status(f"Logs exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs: {e}")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Run the configurator"""
        self.refresh_logs()
        self.root.mainloop()

if __name__ == "__main__":
    app = BotConfigurator()
    app.run()
