#!/usr/bin/env python3
"""
OAuth Authenti        # If there are no valid credentials, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("🔄 Refreshing expired token...")
                try:
                    self.creds.refresh(Request())
                    print("✅ Token refreshed successfully")
                    # Save refreshed credentials immediately
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(self.creds, token)
                except Exception as e:
                    print(f"❌ Token refresh failed: {e}")
                    print("🤖 Attempting automatic credential renewal...")
                    return self._auto_refresh_credentials()
            else:
                print("🤖 No valid credentials, attempting automatic renewal...")
                return self._auto_refresh_credentials()or Google APIs
This replaces service account authentication with user OAuth
"""

import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import gspread
from google.oauth2.credentials import Credentials

class OAuthManager:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        self.creds = None
        self.token_file = 'token.pickle'
        self.credentials_file = 'oauth_credentials.json'
    
    def authenticate(self):
        """Authenticate using OAuth and return credentials"""
        print("🔐 Starting OAuth authentication...")
        
        # Check if credentials file exists
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"❌ {self.credentials_file} not found!\n"
                "Please download OAuth credentials from Google Cloud Console.\n"
                "Run: python scripts/oauth_setup_guide.py for instructions."
            )
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            print("📄 Loading existing authentication token...")
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no valid credentials, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("🔄 Refreshing expired token...")
                try:
                    self.creds.refresh(Request())
                    print("✅ Token refreshed successfully")
                except Exception as e:
                    print(f"❌ Token refresh failed: {e}")
                    print("�️ Removing expired token file...")
                    self._remove_token_file()
                    print("�🔄 Starting new authentication flow...")
                    self._run_oauth_flow()
            else:
                print("🆕 Starting new authentication flow...")
                self._run_oauth_flow()
            
            # Save credentials for future use
            print("💾 Saving authentication token...")
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        
        print("✅ OAuth authentication successful!")
        return self.creds
    
    def _run_oauth_flow(self):
        """Run the OAuth flow to get new credentials"""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, self.SCOPES)
        
        # Try to run local server first, fallback to manual entry
        try:
            print("🌐 Starting local server for authentication...")
            self.creds = flow.run_local_server(port=0)
        except Exception as e:
            print(f"⚠️  Local server failed: {e}")
            print("📝 Falling back to manual authentication...")
            self.creds = flow.run_console()
    
    def _remove_token_file(self):
        """Remove the expired token file"""
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
                print(f"🗑️ Removed expired token file: {self.token_file}")
        except Exception as e:
            print(f"⚠️ Could not remove token file: {e}")
    
    def _auto_refresh_credentials(self):
        """Automatically refresh credentials using a backup refresh token approach"""
        print("🤖 Attempting automatic credential renewal...")
        
        # Try to create new credentials using the original OAuth flow silently
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.SCOPES)
            
            # Set up for automatic approval (this will work if user previously approved)
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            
            # Try to use cached approval if available
            print("🔄 Attempting silent credential renewal...")
            
            # For automatic operation, we'll try to reuse any existing refresh token differently
            if self.creds and hasattr(self.creds, 'refresh_token') and self.creds.refresh_token:
                # Create fresh credentials with the same refresh token
                from google.oauth2.credentials import Credentials
                
                new_creds = Credentials(
                    token=None,  # Will be refreshed
                    refresh_token=self.creds.refresh_token,
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=self._get_client_id(),
                    client_secret=self._get_client_secret(),
                    scopes=self.SCOPES
                )
                
                # Try refreshing the new credentials object
                new_creds.refresh(Request())
                self.creds = new_creds
                
                print("✅ Automatic credential renewal successful!")
                
                # Save the renewed credentials
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
                
                return self.creds
            else:
                raise Exception("No refresh token available for automatic renewal")
                
        except Exception as e:
            print(f"❌ Automatic renewal failed: {e}")
            print("🔄 Falling back to manual authentication...")
            self._remove_token_file()
            self._run_oauth_flow()
            
            # Save credentials for future use
            print("💾 Saving authentication token...")
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
            
            return self.creds
    
    def _get_client_id(self):
        """Extract client ID from credentials file"""
        try:
            with open(self.credentials_file, 'r') as f:
                creds_data = json.load(f)
                return creds_data['installed']['client_id']
        except Exception:
            return None
    
    def _get_client_secret(self):
        """Extract client secret from credentials file"""
        try:
            with open(self.credentials_file, 'r') as f:
                creds_data = json.load(f)
                return creds_data['installed']['client_secret']
        except Exception:
            return None
    
    def reset_authentication(self):
        """Reset authentication by removing stored tokens and re-authenticating"""
        print("🔄 Resetting OAuth authentication...")
        self._remove_token_file()
        self.creds = None
        return self.authenticate()
    
    def get_drive_service(self):
        """Get authenticated Google Drive service"""
        if not self.creds:
            self.authenticate()
        return build('drive', 'v3', credentials=self.creds)
    
    def get_sheets_service(self):
        """Get authenticated Google Sheets service"""
        if not self.creds:
            self.authenticate()
        return build('sheets', 'v4', credentials=self.creds)
    
    def get_gspread_client(self):
        """Get authenticated gspread client"""
        if not self.creds:
            self.authenticate()
        return gspread.authorize(self.creds)

# Global instance
oauth_manager = OAuthManager()

if __name__ == "__main__":
    # Test OAuth setup
    try:
        print("🧪 Testing OAuth authentication...")
        creds = oauth_manager.authenticate()
        
        print("🔧 Testing Google Drive access...")
        drive = oauth_manager.get_drive_service()
        about = drive.about().get(fields='user').execute()
        user_email = about['user']['emailAddress']
        print(f"✅ Authenticated as: {user_email}")
        
        print("📊 Testing Google Sheets access...")
        sheets_client = oauth_manager.get_gspread_client()
        print("✅ Google Sheets access confirmed")
        
        print("\n🎉 OAuth setup complete!")
        print("Your bot can now use your personal Google account storage.")
        
    except Exception as e:
        print(f"❌ OAuth setup failed: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure oauth_credentials.json is in the telebot folder")
        print("2. Check that you've enabled Google Drive & Sheets APIs")
        print("3. Verify OAuth consent screen is configured")
        print("4. Run: python scripts/oauth_setup_guide.py for help")
