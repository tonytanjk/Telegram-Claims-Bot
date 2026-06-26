#!/usr/bin/env python3
"""
Reset OAuth Authentication Script
Use this when your Google OAuth token has expired or been revoked.
"""

import os
import sys

def reset_oauth_authentication():
    """Reset OAuth authentication by removing expired tokens"""
    print("🔄 Resetting OAuth Authentication...")
    
    token_file = 'token.pickle'
    
    # Remove existing token file
    if os.path.exists(token_file):
        try:
            os.remove(token_file)
            print(f"✅ Removed expired token file: {token_file}")
        except Exception as e:
            print(f"❌ Error removing token file: {e}")
            return False
    else:
        print("ℹ️  No token file found to remove")
    
    # Import and reset OAuth manager
    try:
        from services.oauth_manager import oauth_manager
        print("🔐 Starting fresh authentication...")
        
        # Authenticate with fresh credentials
        creds = oauth_manager.reset_authentication()
        
        if creds and creds.valid:
            print("✅ Authentication reset successful!")
            print("🎉 Your bot should now work with Google services again.")
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during authentication reset: {e}")
        print("\n💡 Troubleshooting steps:")
        print("1. Make sure 'oauth_credentials.json' exists in the telebot folder")
        print("2. Check that Google Drive & Sheets APIs are enabled")
        print("3. Verify your OAuth consent screen is properly configured")
        print("4. Make sure you have internet connection")
        return False

if __name__ == "__main__":
    print("🔧 OAuth Authentication Reset Tool")
    print("=" * 40)
    
    # Check if credentials file exists
    if not os.path.exists('oauth_credentials.json'):
        print("❌ oauth_credentials.json not found!")
        print("Please download OAuth credentials from Google Cloud Console first.")
        sys.exit(1)
    
    success = reset_oauth_authentication()
    
    if success:
        print("\n🚀 You can now restart your bot!")
    else:
        print("\n💡 If problems persist, check the OAuth setup guide or contact support.")
    
    input("\nPress Enter to exit...")
