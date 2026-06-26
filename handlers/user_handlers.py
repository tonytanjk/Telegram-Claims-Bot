from telegram import Update, InputFile
from telegram.ext import ContextTypes
from utils.auth import is_allowed, is_admin, get_user_sheet_name
from utils.helpers import get_user_display_name
from services.google_services import google_services
from io import StringIO, BytesIO
import csv
import logging
import zipfile
import os
import tempfile
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

def format_expense_row_simplified(row):
    """Format a row for display with the new 4-column structure."""
    if len(row) < 4:
        return "Invalid row data"
    
    date = row[0]
    description = row[1]
    amount_str = row[2]
    receipt = row[3]
    
    # Clean the amount string
    amount_str = amount_str.strip().replace('$', '').replace(',', '')
    try:
        amount = float(amount_str)
        formatted_amount = "${:.2f}".format(amount)
    except (ValueError, TypeError):
        formatted_amount = "$0.00"  # Fallback for invalid amounts
        logger.warning(f"Invalid amount format: {amount_str}")
    
    return f"📅 Date: {date}\n💰 Amount: {formatted_amount}\n📝 Description: {description}\n📎 Receipt: {receipt}"

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the last 5 expenses for the user."""
    user = update.message.from_user
    username = user.username or ""
    if not is_allowed(username):
        display_name = get_user_display_name(user)
        await update.message.reply_text(f"❌ Sorry {display_name}, you are not authorized.")
        return
    display_name = get_user_display_name(user)
    try:
        status_message = await update.message.reply_text("📋 Retrieving your expense history...")
        # Get user's assigned sheet
        user_sheet = get_user_sheet_name(username)
        user_rows = google_services.get_user_sheet_data(user_sheet)
        
        # user_rows already filtered to only contain data rows (7-15)
        if not user_rows:
            await update.message.reply_text(f"Hello {display_name}, no history found for you.")
            return
        
        last5 = user_rows[-5:]
        msgs = [f"📜 Hello {display_name}, here are your last 5 expenses:"]
        for i, r in enumerate(last5, 1):
            formatted = format_expense_row_simplified(r)
            msgs.append(f"\n{i}. {formatted}")
            msgs.append("---")
        await update.message.reply_text("\n".join(msgs))
    except Exception as e:
        logger.error(f"Error in /history: {e}")
        await update.message.reply_text("❌ Failed to fetch history.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send all users' expenses as separate Excel files in a ZIP archive (admin only, preserves formatting)."""
    user = update.message.from_user
    username = user.username or ""
    if not is_admin(username):
        display_name = get_user_display_name(user)
        await update.message.reply_text(f"❌ Sorry {display_name}, only admins can download the spreadsheet.")
        return
    display_name = get_user_display_name(user)
    
    try:
        status_message = await update.message.reply_text("🔄 Preparing expense sheets for download...\nThis may take a moment...")
        # Get all sheets
        all_sheets = google_services.list_all_sheets()
        if not all_sheets:
            await status_message.edit_text("❌ No sheets found in the spreadsheet.")
            return
        
        # Filter out the template sheet
        user_sheets = [sheet for sheet in all_sheets if sheet != "TEMPLATE"]
        
        if not user_sheets:
            await update.message.reply_text("No user sheets found in the spreadsheet.")
            return
        
        await update.message.reply_text(f"📊 Preparing download for {len(user_sheets)} user sheets...")
        
        # Create temporary directory for files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Get current month and year for folder organization
            current_date = datetime.now()
            current_month_year = current_date.strftime("%B_%Y")  # e.g., "July_2025"
            current_month_folder = current_date.strftime("%Y-%m")  # Format used in Google Drive: "2025-07"
            
            # Create zip file path
            zip_path = os.path.join(temp_dir, f"{current_month_year}_Claims.zip")
            
            # Create receipts directory for photos
            receipts_dir = os.path.join(temp_dir, "receipts")
            
            # Update status
            await status_message.edit_text("📊 Downloading Excel sheets and receipt photos...\nThis may take a moment...")
            
            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                success_count = 0
                
                # Add Excel sheets to ZIP
                for sheet_name in user_sheets:
                    try:
                        # Create Excel file for each user
                        xlsx_filename = f"IGNITE GAMING_CLAIMS_{sheet_name}.xlsx"
                        xlsx_path = os.path.join(temp_dir, xlsx_filename)
                        
                        # Export user sheet as Excel (preserves formatting)
                        if google_services.export_user_sheet_as_excel(sheet_name, xlsx_path):
                            # Add to ZIP in sheets folder
                            zipf.write(xlsx_path, f"excel_sheets/{xlsx_filename}")
                            success_count += 1
                            print(f"✅ Successfully exported: {sheet_name}")
                        else:
                            print(f"❌ Failed to export: {sheet_name}")
                    
                    except Exception as e:
                        logger.error(f"Error processing sheet {sheet_name}: {e}")
                        continue
                
                # Download and add receipt photos to ZIP (current month only)
                try:
                    await status_message.edit_text("📸 Downloading current month's receipt photos from Google Drive...")
                    
                    # Download photos only from current month folder
                    month_receipts_dir = os.path.join(receipts_dir, current_month_folder)
                    total_photos = google_services.download_photos_from_month_folder(current_month_folder, month_receipts_dir)
                    
                    # Add photos to ZIP under receipts/{current_month}/ folder
                    if total_photos > 0:
                        for filename in os.listdir(month_receipts_dir):
                            file_path = os.path.join(month_receipts_dir, filename)
                            zipf.write(file_path, f"receipts/{current_month_folder}/{filename}")
                    
                    print(f"✅ Downloaded {total_photos} receipt photos from {current_month_folder}")
                    
                except Exception as e:
                    logger.error(f"Error downloading photos: {e}")
                    total_photos = 0
                
            if success_count == 0:
                await update.message.reply_text("❌ Failed to export any user sheets.")
                return
            
            # Format current month and year for filename
            current_date = datetime.now()
            month_year = current_date.strftime("%B_%Y")  # e.g., "July_2025"
            zip_filename = f"{month_year}_Claims.zip"
            
            # Send ZIP file with updated caption
            with open(zip_path, 'rb') as zip_file:
                caption = (f"📊 Claims Package for {month_year}\n"
                          f"📋 {success_count} Excel sheets\n"
                          f"📸 {total_photos} receipt photos (current month)\n"
                          f"👤 Downloaded by {display_name}")
                
                await update.message.reply_document(
                    document=InputFile(zip_file, filename=zip_filename),
                    caption=caption
                )
    
    except Exception as e:
        logger.error(f"Error in /download: {e}")
        await update.message.reply_text("❌ Failed to download expenses.")

def create_combined_csv(user_sheets: list, output_path: str) -> bool:
    """Create a combined CSV file with all users' data."""
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header with USER column
            writer.writerow(["USER", "DATE", "DESCRIPTION/EXPENSES", "AMOUNT", "ATTACHED RECEIPT (YES/NO)"])
            
            # Process each user sheet
            for sheet_name in user_sheets:
                try:
                    sheet_data = google_services.get_user_sheet_data(sheet_name)
                    for row in sheet_data:
                        if len(row) >= 4 and any(cell.strip() for cell in row if cell):  # Skip empty rows
                            # Add user name as first column
                            formatted_row = [sheet_name] + row[:4]
                            writer.writerow(formatted_row)
                except Exception as e:
                    logger.error(f"Error reading sheet {sheet_name} for combined CSV: {e}")
                    continue
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating combined CSV: {e}")
        return False

