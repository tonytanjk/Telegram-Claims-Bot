# Telegram Bot - OAuth Reset Tool (PowerShell)
# Use this when you get "Token has been expired or revoked" errors

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   OAUTH TOKEN RESET TOOL" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This tool will reset your expired Google OAuth token" -ForegroundColor Yellow
Write-Host ""

# Get current directory
$BOT_DIR = $PSScriptRoot
$PYTHON_EXE = Join-Path $BOT_DIR "python\python.exe"

# Set environment variables
$env:PYTHONPATH = "$BOT_DIR;$BOT_DIR\python\Lib\site-packages;$BOT_DIR\python\Lib"
$env:PYTHONHOME = "$BOT_DIR\python"

# Change to bot directory
Set-Location $BOT_DIR

# Check if embedded Python exists
if (-not (Test-Path $PYTHON_EXE)) {
    Write-Host "❌ ERROR: Embedded Python not found: $PYTHON_EXE" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for OAuth credentials
$OAUTH_CREDS = Join-Path $BOT_DIR "oauth_credentials.json"
if (-not (Test-Path $OAUTH_CREDS)) {
    Write-Host "❌ ERROR: OAuth credentials not found" -ForegroundColor Red
    Write-Host "Make sure oauth_credentials.json is in this directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🔄 Starting OAuth token reset..." -ForegroundColor Cyan
Write-Host ""

try {
    & $PYTHON_EXE "$BOT_DIR\reset_auth.py"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ OAuth reset completed successfully!" -ForegroundColor Green
        Write-Host "You can now run your bot again." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ OAuth reset failed" -ForegroundColor Red
        Write-Host "Check the error messages above" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error during OAuth reset: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
