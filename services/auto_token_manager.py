"""
Automatic OAuth Token Manager
Handles token refresh automatically without user intervention
"""

import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class AutoTokenManager:
    """Manages automatic token refresh for Google services"""
    
    def __init__(self, oauth_manager):
        self.oauth_manager = oauth_manager
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def with_auto_retry(self, func):
        """Decorator that automatically retries operations with token refresh"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    # Check if it's a token-related error
                    token_errors = [
                        'invalid_grant',
                        'token has been expired',
                        'expired or revoked',
                        'unauthorized',
                        'invalid credentials',
                        'credentials have expired'
                    ]
                    
                    is_token_error = any(token_error in error_str for token_error in token_errors)
                    
                    if is_token_error and attempt < self.max_retries - 1:
                        logger.warning(f"Token error detected (attempt {attempt + 1}/{self.max_retries}): {e}")
                        logger.info("🔄 Attempting automatic token refresh...")
                        
                        try:
                            # Force refresh credentials
                            self.oauth_manager._initialized = False
                            
                            # Wait a bit before retry
                            time.sleep(self.retry_delay * (attempt + 1))
                            
                            # Re-authenticate
                            self.oauth_manager.authenticate()
                            logger.info("✅ Token refreshed automatically")
                            
                            # Continue to next attempt
                            continue
                            
                        except Exception as refresh_error:
                            logger.error(f"❌ Auto-refresh failed: {refresh_error}")
                            
                    else:
                        # Not a token error or max retries reached
                        break
            
            # If we get here, all retries failed
            logger.error(f"❌ Operation failed after {self.max_retries} attempts: {last_exception}")
            raise last_exception
        
        return wrapper

# Global auto token manager instance
auto_token_manager = None

def init_auto_token_manager(oauth_manager):
    """Initialize the global auto token manager"""
    global auto_token_manager
    auto_token_manager = AutoTokenManager(oauth_manager)
    return auto_token_manager

def auto_retry(func):
    """Decorator for automatic retry with token refresh"""
    def wrapper(*args, **kwargs):
        if auto_token_manager:
            return auto_token_manager.with_auto_retry(func)(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper
