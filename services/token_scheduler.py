"""
Token Refresh Scheduler
Automatically refreshes OAuth tokens before they expire
"""

import threading
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TokenRefreshScheduler:
    """Automatically refreshes OAuth tokens before expiration"""
    
    def __init__(self, oauth_manager, refresh_interval_hours=1):
        self.oauth_manager = oauth_manager
        self.refresh_interval = refresh_interval_hours * 3600  # Convert to seconds
        self.running = False
        self.thread = None
        self.min_token_lifetime = 300  # Refresh if token expires in 5 minutes
    
    def start(self):
        """Start the token refresh scheduler"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.thread.start()
        logger.info("🔄 Token refresh scheduler started")
    
    def stop(self):
        """Stop the token refresh scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🛑 Token refresh scheduler stopped")
    
    def _refresh_loop(self):
        """Main refresh loop that runs in background"""
        while self.running:
            try:
                self._check_and_refresh_token()
            except Exception as e:
                logger.error(f"❌ Error in token refresh loop: {e}")
            
            # Wait for next check
            time.sleep(self.refresh_interval)
    
    def _check_and_refresh_token(self):
        """Check if token needs refresh and refresh if necessary"""
        try:
            if not self.oauth_manager.creds:
                logger.debug("No credentials loaded, skipping refresh check")
                return
            
            # Check if token is valid and not expiring soon
            if self.oauth_manager.creds.valid:
                # Check if token will expire soon
                if hasattr(self.oauth_manager.creds, 'expiry') and self.oauth_manager.creds.expiry:
                    time_until_expiry = (self.oauth_manager.creds.expiry - datetime.utcnow()).total_seconds()
                    
                    if time_until_expiry < self.min_token_lifetime:
                        logger.info(f"🔄 Token expires in {time_until_expiry:.0f} seconds, refreshing...")
                        self._perform_refresh()
                    else:
                        logger.debug(f"Token valid for {time_until_expiry:.0f} more seconds")
                else:
                    logger.debug("Token has no expiry time, skipping refresh")
            else:
                logger.info("🔄 Token is invalid, refreshing...")
                self._perform_refresh()
                
        except Exception as e:
            logger.error(f"❌ Error checking token status: {e}")
    
    def _perform_refresh(self):
        """Perform the actual token refresh"""
        try:
            if self.oauth_manager.creds and hasattr(self.oauth_manager.creds, 'refresh_token') and self.oauth_manager.creds.refresh_token:
                from google.auth.transport.requests import Request
                import pickle
                
                # Refresh the token
                self.oauth_manager.creds.refresh(Request())
                logger.info("✅ Token refreshed successfully by scheduler")
                
                # Save the refreshed token
                with open(self.oauth_manager.token_file, 'wb') as token:
                    pickle.dump(self.oauth_manager.creds, token)
                logger.debug("💾 Refreshed token saved to file")
                
            else:
                logger.warning("⚠️ No refresh token available for automatic refresh")
                
        except Exception as e:
            logger.error(f"❌ Failed to refresh token: {e}")
            # Don't raise the exception, just log it

# Global scheduler instance
token_scheduler = None

def start_token_scheduler(oauth_manager, refresh_interval_hours=1):
    """Start the global token refresh scheduler"""
    global token_scheduler
    
    if token_scheduler:
        token_scheduler.stop()
    
    token_scheduler = TokenRefreshScheduler(oauth_manager, refresh_interval_hours)
    token_scheduler.start()
    return token_scheduler

def stop_token_scheduler():
    """Stop the global token refresh scheduler"""
    global token_scheduler
    
    if token_scheduler:
        token_scheduler.stop()
        token_scheduler = None
