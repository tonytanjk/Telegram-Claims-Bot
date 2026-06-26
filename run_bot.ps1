# Telegram Bot - Portable Edition (PowerShell)
# Windows 11 Compatible Launcher

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   TELEGRAM BOT - PORTABLE EDITION" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This package does NOT require Python installation!" -ForegroundColor Green
Write-Host "Uses embedded Python distribution" -ForegroundColor Green
Write-Host ""

# Get current directory
$BOT_DIR = $PSScriptRoot
$PYTHON_EXE = Join-Path $BOT_DIR "python\python.exe"

# Set environment variables and change to bot directory
$env:PYTHONPATH = "$BOT_DIR;$BOT_DIR\python\Lib\site-packages;$BOT_DIR\python\Lib"
$env:PYTHONHOME = "$BOT_DIR\python"
$env:PATH = "$BOT_DIR\python;$BOT_DIR\python\Scripts;" + $env:PATH

# Change to bot directory for relative imports
Set-Location $BOT_DIR

Write-Host "Bot directory: $BOT_DIR" -ForegroundColor Yellow
Write-Host "Python executable: $PYTHON_EXE" -ForegroundColor Yellow
Write-Host ""

# Check if embedded Python exists
if (-not (Test-Path $PYTHON_EXE)) {
    Write-Host "❌ ERROR: Embedded Python not found: $PYTHON_EXE" -ForegroundColor Red
    Write-Host "Make sure the python folder is in the same directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ SUCCESS: Embedded Python found" -ForegroundColor Green

# Check for bot script
$BOT_SCRIPT = Join-Path $BOT_DIR "bot.py"
if (-not (Test-Path $BOT_SCRIPT)) {
    Write-Host "❌ ERROR: Bot script not found: $BOT_SCRIPT" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ SUCCESS: Bot script found" -ForegroundColor Green

# Check for OAuth credentials
$OAUTH_CREDS = Join-Path $BOT_DIR "oauth_credentials.json"
if (-not (Test-Path $OAUTH_CREDS)) {
    Write-Host "❌ ERROR: OAuth credentials not found" -ForegroundColor Red
    Write-Host "Make sure oauth_credentials.json is in this directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ SUCCESS: OAuth credentials found" -ForegroundColor Green
Write-Host ""

# Start the bot
Write-Host "🚀 Starting Telegram Bot..." -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

try {
    & $PYTHON_EXE "$BOT_DIR\bot.py"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ Bot exited with error code: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Check the error messages above" -ForegroundColor Red
    } else {
        Write-Host ""
        Write-Host "✅ Bot stopped normally" -ForegroundColor Green
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error starting bot: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Read-Host "Press Enter to exit"
}
