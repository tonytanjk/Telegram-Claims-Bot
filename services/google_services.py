import gspread
import os
import csv
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import GOOGLE_SCOPE, SPREADSHEET_NAME, DRIVE_FOLDER_ID
from services.oauth_manager import oauth_manager
from services.auto_token_manager import init_auto_token_manager, auto_retry

from typing import List, Any

class GoogleServices:
    """
    Service class for Google Sheets and Drive operations.
    """
    def __init__(self):
        self.creds = None
        self.client = None
        self.sheet = None
        self.drive_service = None
        self._initialized = False
        
        # Initialize auto token manager for seamless token refresh
        self.auto_token_manager = init_auto_token_manager(oauth_manager)

    def _initialize(self):
        """Initialize Google Services connections lazily."""
        if self._initialized:
            return True
        
        try:
            print("🔐 Initializing OAuth authentication...")
            
            # Use OAuth authentication instead of service account
            self.creds = oauth_manager.authenticate()
            
            # Initialize gspread client
            self.client = oauth_manager.get_gspread_client()
            print("✅ Google Sheets client authorized with OAuth")
            
            # Initialize Drive service
            self.drive_service = oauth_manager.get_drive_service()
            print("✅ Google Drive service initialized with OAuth")
            
            # Try to find the spreadsheet in the specific folder first
            spreadsheet_id = self._find_spreadsheet_in_folder(DRIVE_FOLDER_ID, SPREADSHEET_NAME)
            
            if spreadsheet_id:
                # Open by ID instead of name
                spreadsheet = self.client.open_by_key(spreadsheet_id)
                print(f"✅ Spreadsheet '{SPREADSHEET_NAME}' opened by ID from folder")
                
                # Get the first worksheet (don't assume it's called 'Sheet1')
                worksheets = spreadsheet.worksheets()
                if worksheets:
                    self.sheet = worksheets[0]
                    print(f"✅ Using worksheet: '{self.sheet.title}'")
                else:
                    print("⚠️  No worksheets found in spreadsheet")
                    self.sheet = None
            else:
                # Set to None - we'll handle this in the _get_spreadsheet method
                print(f"⚠️  Spreadsheet '{SPREADSHEET_NAME}' not found in folder, will retry on first use")
                self.sheet = None
            
            self._initialized = True
            return True
            
        except FileNotFoundError as e:
            print(f"❌ OAuth credentials file not found: {e}")
            print("💡 Please run: python scripts/oauth_setup_guide.py")
            return False
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"❌ Spreadsheet '{SPREADSHEET_NAME}' not found or not accessible")
            print("Please check:")
            print("1. SPREADSHEET_NAME in config.py is correct")
            print("2. You have access to the spreadsheet")
            print("3. Spreadsheet is in the specified DRIVE_FOLDER_ID")
            return False
        except Exception as e:
            error_str = str(e).lower()
            print(f"❌ Error initializing Google Services: {e}")
            print(f"Error type: {type(e).__name__}")
            
            # Check for OAuth token errors
            if any(token_error in error_str for token_error in ['invalid_grant', 'token has been expired', 'expired or revoked']):
                print("\n🔑 OAuth Token Error Detected!")
                print("Your Google authentication token has expired or been revoked.")
                print("\n💡 To fix this:")
                print("1. Run: reset_oauth.ps1 (Windows) or python reset_auth.py")
                print("2. Complete the authentication flow")
                print("3. Restart your bot")
                print("\nAlternatively, delete token.pickle and restart the bot.")
            else:
                print("Please check:")
                print("1. oauth_credentials.json file exists and is valid")
                print("2. SPREADSHEET_NAME in config.py is correct")
                print("3. You have access to the spreadsheet")
                print("4. Internet connection is working")
                print("5. Google Drive & Sheets APIs are enabled")
            return False

    def _ensure_initialized(self):
        """Ensure Google Services are initialized before use."""
        if not self._initialize():
            raise Exception("Google Services not initialized. Please check your configuration.")

    @auto_retry
    def append_to_sheet(self, row_data: List[Any]) -> Any:
        """Append a row to the Google Sheet."""
        self._ensure_initialized()
        return self.sheet.append_row(row_data)

    @auto_retry
    def get_all_sheet_data(self) -> List[List[str]]:
        """Get all data from the Google Sheet."""
        self._ensure_initialized()
        return self.sheet.get_all_values()

    @auto_retry
    def delete_sheet_row(self, row_num: int) -> Any:
        """Delete a row from the Google Sheet by row number."""
        self._ensure_initialized()
        return self.sheet.delete_rows(row_num)

    @auto_retry
    def upload_to_drive(self, file_path: str, file_name: str) -> str:
        """Upload a file to Google Drive and return its shareable URL."""
        self._ensure_initialized()
        file_metadata = {
            'name': file_name,
            'parents': [DRIVE_FOLDER_ID],
        }
        media = MediaFileUpload(file_path, mimetype='image/jpeg')
        uploaded_file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True,
            supportsTeamDrives=True
        ).execute()
        self.drive_service.permissions().create(
            fileId=uploaded_file['id'],
            body={'role': 'reader', 'type': 'anyone'},
            supportsAllDrives=True,
            supportsTeamDrives=True
        ).execute()
        return f"https://drive.google.com/file/d/{uploaded_file['id']}/view?usp=sharing"

    def find_expenses_by_user(self, username: str) -> List[List[str]]:
        """Return all expenses for a given username."""
        self._ensure_initialized()
        return [row for row in self.get_all_sheet_data()[1:] if row[0] == username]

    def get_summary_by_user(self) -> dict:
        """Return a summary dict of total amount by user."""
        self._ensure_initialized()
        rows = self.get_all_sheet_data()[1:]
        summary = {}
        for row in rows:
            user_row, _, _, _, amount, _ = row
            try:
                amt = float(amount)
            except Exception:
                amt = 0
            summary[user_row] = summary.get(user_row, 0) + amt
        return summary

    def get_or_create_month_folder(self, parent_folder_id: str, month_folder_name: str) -> str:
        """Get the folder ID for the given month under parent, or create it if it doesn't exist."""
        self._ensure_initialized()
        # Search for folder
        query = f"'{parent_folder_id}' in parents and name = '{month_folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.drive_service.files().list(q=query, fields="files(id, name)", supportsAllDrives=True, supportsTeamDrives=True).execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
        # Create folder if not found
        file_metadata = {
            'name': month_folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = self.drive_service.files().create(body=file_metadata, fields='id', supportsAllDrives=True, supportsTeamDrives=True).execute()
        return folder['id']

    def upload_to_drive_monthly(self, file_path: str, file_name: str, month_folder_name: str) -> str:
        """Upload a file to a month folder on Google Drive, creating the folder if needed."""
        self._ensure_initialized()
        folder_id = self.get_or_create_month_folder(DRIVE_FOLDER_ID, month_folder_name)
        file_metadata = {
            'name': file_name,
            'parents': [folder_id],
        }
        media = MediaFileUpload(file_path, mimetype='image/jpeg')
        uploaded_file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True,
            supportsTeamDrives=True
        ).execute()
        self.drive_service.permissions().create(
            fileId=uploaded_file['id'],
            body={'role': 'reader', 'type': 'anyone'},
            supportsAllDrives=True,
            supportsTeamDrives=True
        ).execute()
        return f"https://drive.google.com/file/d/{uploaded_file['id']}/view?usp=sharing"

    def create_user_sheet(self, sheet_name: str, template_sheet_name: str = None) -> bool:
        """Create a new sheet for a user by duplicating an existing template sheet."""
        try:
            self._ensure_initialized()
            # Check if sheet already exists
            try:
                worksheet = self._get_spreadsheet().worksheet(sheet_name)
                return True  # Sheet already exists
            except gspread.exceptions.WorksheetNotFound:
                pass  # Sheet doesn't exist, create it
            except Exception as e:
                print(f"Error checking for existing sheet: {e}")
                return False
            
            spreadsheet = self._get_spreadsheet()
            if not spreadsheet:
                return False
            
            # Find template sheet
            if template_sheet_name is None:
                template_sheet_name = self.find_template_sheet()
            
            # Try to find the template sheet
            template_worksheet = None
            try:
                template_worksheet = spreadsheet.worksheet(template_sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                print(f"Template sheet '{template_sheet_name}' not found. Creating basic sheet instead.")
                # Fallback to creating a basic sheet
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=4)
                headers = ["DATE", "DESCRIPTION/EXPENSES", "AMOUNT", "ATTACHED RECEIPT (YES/NO)"]
                worksheet.update('A6:D6', [headers])
                worksheet.format("A6:D6", {"textFormat": {"bold": True}})
                return True
            
            # Duplicate the template sheet
            new_worksheet = template_worksheet.duplicate(new_sheet_name=sheet_name)
            
            # Clear the data rows (8-16) in the new sheet, keeping the template structure
            try:
                new_worksheet.batch_clear(['A8:D16'])
            except Exception as e:
                print(f"Warning: Could not clear data rows in new sheet: {e}")
            
            # Clear amount formatting to avoid single quotes
            try:
                new_worksheet.format("C8:C16", {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}})
                print(f"✅ Cleared amount formatting for sheet: {sheet_name}")
            except Exception as e:
                print(f"Warning: Could not clear amount formatting: {e}")
            
            return True
        except Exception as e:
            print(f"Error creating sheet {sheet_name}: {e}")
            return False

    def get_or_create_user_sheet(self, sheet_name: str, template_sheet_name: str = None):
        """Get user sheet or create it if it doesn't exist."""
        try:
            self._ensure_initialized()
            # Try to get existing sheet
            spreadsheet = self._get_spreadsheet()
            if not spreadsheet:
                return self.sheet  # Fallback to main sheet
            worksheet = spreadsheet.worksheet(sheet_name)
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            # Create new sheet
            if self.create_user_sheet(sheet_name, template_sheet_name):
                spreadsheet = self._get_spreadsheet()
                if spreadsheet:
                    return spreadsheet.worksheet(sheet_name)
                else:
                    return self.sheet  # Fallback to main sheet
            else:
                # Fallback to main sheet
                return self.sheet

    @auto_retry
    def append_to_user_sheet(self, sheet_name: str, row_data: List[Any], template_sheet_name: str = None) -> Any:
        """Add a row to a specific user's sheet in the designated range (rows 8-16) and update last upload date."""
        worksheet = self.get_or_create_user_sheet(sheet_name, template_sheet_name)
        
        # Get existing data in rows 8-16
        try:
            existing_data = worksheet.get('A8:D16')
            # Find the first empty row in the range
            target_row = 8
            for i, row in enumerate(existing_data):
                if not any(cell.strip() for cell in row if cell):  # Empty row
                    target_row = 8 + i
                    break
                if i == 8:  # If we've reached row 16 (index 8), we're full
                    target_row = 16
                    break
            else:
                # If no empty row found and we haven't reached the end
                target_row = 8 + len(existing_data)
                if target_row > 16:
                    target_row = 16
                    
            # Update last upload date in B23 (DD/MM/YY format)
            current_date = datetime.now().strftime("%d/%m/%y")
            worksheet.update('B23', [[current_date]], value_input_option='USER_ENTERED')
            
            # Ensure date formatting is applied
            worksheet.format('B23', {
                "numberFormat": {"type": "DATE", "pattern": "dd/mm/yy"}
            })
            
            # Update the specific cell range
            cell_range = f'A{target_row}:D{target_row}'
            worksheet.update(cell_range, [row_data])
            return True
            
        except Exception as e:
            print(f"Error adding to user sheet {sheet_name}: {e}")
            # Fallback to regular append if there's an issue
            return worksheet.append_row(row_data)

    @auto_retry
    def get_user_sheet_data(self, sheet_name: str, template_sheet_name: str = None) -> List[List[str]]:
        """Get data from a specific user's sheet (rows 8-16 only)."""
        try:
            self._ensure_initialized()
            worksheet = self.get_or_create_user_sheet(sheet_name, template_sheet_name)
            # Get only the data rows (8-16)
            data_rows = worksheet.get('A8:D16')
            # Filter out empty rows
            return [row for row in data_rows if any(cell.strip() for cell in row if cell)]
        except Exception as e:
            print(f"Error getting user sheet data: {e}")
            return []

    def delete_user_sheet(self, sheet_name: str) -> bool:
        """Delete a user's sheet."""
        try:
            self._ensure_initialized()
            spreadsheet = self._get_spreadsheet()
            if not spreadsheet:
                return False
            worksheet = spreadsheet.worksheet(sheet_name)
            spreadsheet.del_worksheet(worksheet)
            return True
        except Exception as e:
            print(f"Error deleting sheet {sheet_name}: {e}")
            return False

    @auto_retry
    def list_all_sheets(self) -> List[str]:
        """List all sheets in the spreadsheet."""
        try:
            self._ensure_initialized()
            spreadsheet = self._get_spreadsheet()
            if not spreadsheet:
                return []
            return [ws.title for ws in spreadsheet.worksheets()]
        except Exception as e:
            print(f"Error listing sheets: {e}")
            return []

    def find_template_sheet(self, preferred_names: List[str] = None) -> str:
        """Find the template sheet by checking common names or using the first sheet."""
        if preferred_names is None:
            # Based on the provided URL, look for sheets with claim form structure
            preferred_names = ["CLAIM FORM", "TEMPLATE", "Template", "Sheet1", "IGNITE GAMING SG PTE LTD"]
        
        try:
            self._ensure_initialized()
            spreadsheet = self._get_spreadsheet()
            if not spreadsheet:
                return "Sheet1"
            all_sheets = [ws.title for ws in spreadsheet.worksheets()]
            
            print(f"Available sheets: {all_sheets}")
            
            # Check for preferred names first
            for preferred in preferred_names:
                if preferred in all_sheets:
                    print(f"Found template sheet: {preferred}")
                    return preferred
            
            # If no preferred names found, use the first sheet
            if all_sheets:
                print(f"Using first available sheet: {all_sheets[0]}")
                return all_sheets[0]
            
            return "Sheet1"  # Final fallback
        except Exception as e:
            print(f"Error finding template sheet: {e}")
            return "Sheet1"

    def clear_amount_formatting(self, sheet_name: str) -> bool:
        """Clear formatting from the amount column (column C) in rows 7-15."""
        try:
            self._ensure_initialized()
            worksheet = self.get_or_create_user_sheet(sheet_name)
            
            # Clear formatting from amount column (C7:C15)
            worksheet.format("C7:C15", {"numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}})
            
            return True
        except Exception as e:
            print(f"Error clearing amount formatting: {e}")
            return False

    def _find_spreadsheet_in_folder(self, folder_id: str, spreadsheet_name: str) -> str:
        """Find a spreadsheet by name within a specific folder and return its ID."""
        try:
            # Search for the spreadsheet in the specific folder
            query = f"'{folder_id}' in parents and name = '{spreadsheet_name}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
            results = self.drive_service.files().list(q=query, fields="files(id, name)", supportsAllDrives=True, supportsTeamDrives=True).execute()
            files = results.get('files', [])
            
            if files:
                spreadsheet_id = files[0]['id']
                print(f"Found spreadsheet '{spreadsheet_name}' with ID: {spreadsheet_id}")
                return spreadsheet_id
            else:
                print(f"Spreadsheet '{spreadsheet_name}' not found in folder {folder_id}")
                return None
                
        except Exception as e:
            print(f"Error searching for spreadsheet: {e}")
            return None

    def _get_spreadsheet(self):
        """Get the spreadsheet object, searching in folder first if needed."""
        try:
            # First try to find in the specific folder
            spreadsheet_id = self._find_spreadsheet_in_folder(DRIVE_FOLDER_ID, SPREADSHEET_NAME)
            
            if spreadsheet_id:
                return self.client.open_by_key(spreadsheet_id)
            else:
                # Fallback: try to open by name
                return self.client.open(SPREADSHEET_NAME)
                
        except Exception as e:
            print(f"Error getting spreadsheet: {e}")
            return None

    def export_user_sheet_as_excel(self, sheet_name: str, output_path: str) -> bool:
        """Export a user's sheet as an Excel file maintaining formatting."""
        try:
            self._ensure_initialized()
            
            # Get the spreadsheet
            spreadsheet = self._get_spreadsheet()
            if not spreadsheet:
                return False
            
            # Get the worksheet
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Get the spreadsheet ID
            spreadsheet_id = spreadsheet.id
            
            # Get the worksheet ID
            worksheet_id = worksheet.id
            
            # Export as Excel using Google Drive API
            export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=xlsx&gid={worksheet_id}"
            
            # Get fresh credentials to ensure access token is valid
            fresh_creds = oauth_manager.creds
            if not fresh_creds or not fresh_creds.valid:
                fresh_creds = oauth_manager.authenticate()
            
            # Make the request with proper token attribute
            import requests
            response = requests.get(export_url, headers={'Authorization': f'Bearer {fresh_creds.token}'})
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"Failed to export sheet: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error exporting sheet {sheet_name}: {e}")
            return False

    def export_user_sheet_as_csv(self, sheet_name: str, output_path: str) -> bool:
        """Export a user's sheet as a CSV file."""
        try:
            self._ensure_initialized()
            
            # Get user sheet data
            sheet_data = self.get_user_sheet_data(sheet_name)
            
            if not sheet_data:
                # Create empty CSV with headers
                with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["DATE", "DESCRIPTION/EXPENSES", "AMOUNT", "ATTACHED RECEIPT (YES/NO)"])
                return True
            
            # Write CSV file
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["DATE", "DESCRIPTION/EXPENSES", "AMOUNT", "ATTACHED RECEIPT (YES/NO)"])
                
                # Write data rows
                for row in sheet_data:
                    # Ensure we have exactly 4 columns
                    formatted_row = row[:4] if len(row) >= 4 else row + [''] * (4 - len(row))
                    writer.writerow(formatted_row)
            
            return True
            
        except Exception as e:
            print(f"Error exporting sheet {sheet_name} as CSV: {e}")
            return False

    def clear_sheet_data(self, sheet_name: str) -> bool:
        """Clear only the data in rows 8-16 while preserving all formatting."""
        try:
            self._ensure_initialized()
            worksheet = self.get_or_create_user_sheet(sheet_name)
            
            # Get current formatting
            current_data = worksheet.get('A8:D16', value_render_option='FORMULA')
            if current_data:
                # Create empty data array with same dimensions
                num_rows = len(current_data)
                empty_data = [[''] * 4 for _ in range(num_rows)]
                
                # Update only the values, preserving formatting
                worksheet.update('A8:D16', empty_data, value_input_option='RAW')
            
            return True
        except Exception as e:
            print(f"Error clearing sheet {sheet_name}: {e}")
            return False

    def download_photos_from_month_folder(self, month_folder_name: str, output_dir: str) -> int:
        """Download all photos from a specific month folder on Google Drive."""
        try:
            self._ensure_initialized()
            folder_id = self.get_or_create_month_folder(DRIVE_FOLDER_ID, month_folder_name)
            
            # List all image files in the month folder
            query = f"'{folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png' or mimeType='image/jpg')"
            results = self.drive_service.files().list(q=query, fields="files(id, name)", supportsAllDrives=True, supportsTeamDrives=True).execute()
            files = results.get('files', [])
            
            downloaded_count = 0
            os.makedirs(output_dir, exist_ok=True)
            
            for file in files:
                try:
                    # Download the file
                    file_id = file['id']
                    file_name = file['name']
                    
                    # Get file content
                    file_content = self.drive_service.files().get_media(fileId=file_id, supportsAllDrives=True, supportsTeamDrives=True).execute()
                    
                    # Save to local directory
                    local_path = os.path.join(output_dir, file_name)
                    with open(local_path, 'wb') as f:
                        f.write(file_content)
                    
                    downloaded_count += 1
                    print(f"✅ Downloaded: {file_name}")
                    
                except Exception as e:
                    print(f"❌ Failed to download {file.get('name', 'unknown')}: {e}")
                    continue
            
            return downloaded_count
            
        except Exception as e:
            print(f"Error downloading photos from month folder {month_folder_name}: {e}")
            return 0

    def list_all_month_folders(self) -> list:
        """List all month folders (YYYY-MM format) in the main drive folder."""
        try:
            self._ensure_initialized()
            query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder'"
            results = self.drive_service.files().list(q=query, fields="files(name)", supportsAllDrives=True, supportsTeamDrives=True).execute()
            folders = results.get('files', [])
            
            # Filter for month folders (YYYY-MM format)
            month_folders = []
            for folder in folders:
                folder_name = folder['name']
                # Check if folder name matches YYYY-MM pattern
                if len(folder_name) == 7 and folder_name[4] == '-' and folder_name[:4].isdigit() and folder_name[5:].isdigit():
                    month_folders.append(folder_name)
            
            return sorted(month_folders)
            
        except Exception as e:
            print(f"Error listing month folders: {e}")
            return []

# Global instance
google_services = GoogleServices()
