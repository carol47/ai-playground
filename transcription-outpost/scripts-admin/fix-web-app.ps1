#!/usr/bin/env pwsh

Write-Host "🔧 Fixing Web Application CSS Issues..." -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Stop any running Node.js processes
Write-Host "1. Stopping Node.js processes..." -ForegroundColor Yellow
try {
    Get-Process node -ErrorAction Stop | Stop-Process -Force
    Write-Host "   ✅ Node.js processes stopped" -ForegroundColor Green
} catch {
    Write-Host "   ℹ️  No Node.js processes running" -ForegroundColor Blue
}

# Navigate to web directory
Set-Location "web"
Write-Host "2. Navigating to web directory..." -ForegroundColor Yellow

# Remove problematic .next directory
Write-Host "3. Cleaning Next.js cache..." -ForegroundColor Yellow
if (Test-Path ".next") {
    try {
        Remove-Item ".next" -Recurse -Force
        Write-Host "   ✅ .next directory removed" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Could not remove .next directory, trying alternative..." -ForegroundColor Red
        # Try using cmd to remove if PowerShell fails
        cmd /c "rmdir /s /q .next"
        Write-Host "   ✅ .next directory removed via cmd" -ForegroundColor Green
    }
} else {
    Write-Host "   ℹ️  .next directory doesn't exist" -ForegroundColor Blue
}

# Clear npm cache
Write-Host "4. Clearing npm cache..." -ForegroundColor Yellow
npm cache clean --force
Write-Host "   ✅ npm cache cleared" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Ready to restart services!" -ForegroundColor Cyan
Write-Host "Run these commands:" -ForegroundColor Yellow
Write-Host "   HTTP:  npm run dev:http" -ForegroundColor White
Write-Host "   HTTPS: npm run dev:https" -ForegroundColor White
Write-Host ""
Write-Host "💡 The CSS should now load properly!" -ForegroundColor Green 