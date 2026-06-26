"""
Runtime OAuth Installer for Executable
This module handles missing OAuth dependencies at runtime
"""

import sys
import subprocess
import os
import importlib

def install_missing_oauth_deps():
    """Install missing OAuth dependencies at runtime"""
    print("🔧 Checking OAuth dependencies...")
    
    required_modules = [
        ('google.auth', 'google-auth'),
        ('google_auth_oauthlib', 'google-auth-oauthlib'),
        ('google.oauth2', 'google-auth'),
        ('googleapiclient', 'google-api-python-client'),
        ('gspread', 'gspread')
    ]
    
    missing_packages = []
    
    for module_name, package_name in required_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name} available")
        except ImportError:
            print(f"❌ {module_name} missing - need to install {package_name}")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"📦 Installing missing packages: {missing_packages}")
        try:
            # Install missing packages
            for package in missing_packages:
                print(f"Installing {package}...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package, "--user"
                ])
            
            print("✅ All OAuth dependencies installed!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("💡 Please manually install:")
            for package in missing_packages:
                print(f"   pip install {package}")
            return False
    else:
        print("✅ All OAuth dependencies available")
        return True

def ensure_oauth_modules():
    """Ensure OAuth modules are available, install if needed"""
    try:
        # Try importing key modules
        import google.auth
        import google_auth_oauthlib
        import gspread
        return True
    except ImportError as e:
        print(f"⚠️  OAuth import failed: {e}")
        print("🔧 Attempting to install missing dependencies...")
        return install_missing_oauth_deps()

if __name__ == "__main__":
    # Test the installer
    ensure_oauth_modules()
