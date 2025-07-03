#!/usr/bin/env pwsh

Write-Host "🔧 Fixing Web Application Permissions..." -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Kill Node.js processes
Write-Host "1. Killing Node.js processes..." -ForegroundColor Yellow
try {
    Get-Process node -ErrorAction Stop | Stop-Process -Force
    Write-Host "   ✅ Node.js processes killed" -ForegroundColor Green
} catch {
    Write-Host "   ℹ️  No Node.js processes running" -ForegroundColor Blue
}

# Navigate to the project directory
$projectPath = "C:\Users\carol\code\ai-playground\transcription-outpost\web"
Write-Host "2. Working with directory: $projectPath" -ForegroundColor Yellow

# Check if .next directory exists
$nextPath = Join-Path $projectPath ".next"
if (Test-Path $nextPath) {
    Write-Host "3. Found .next directory, fixing permissions..." -ForegroundColor Yellow
    
    # Take ownership of the .next directory
    try {
        takeown /F "$nextPath" /R /D Y 2>$null
        Write-Host "   ✅ Took ownership of .next directory" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Could not take ownership (might not be needed)" -ForegroundColor Yellow
    }
    
    # Grant full control to current user
    try {
        icacls "$nextPath" /grant "$env:USERNAME:(F)" /T /Q 2>$null
        Write-Host "   ✅ Granted full permissions to current user" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Could not set permissions" -ForegroundColor Yellow
    }
    
    # Grant full control to Users group
    try {
        icacls "$nextPath" /grant "Users:(F)" /T /Q 2>$null
        Write-Host "   ✅ Granted full permissions to Users group" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Could not set Users permissions" -ForegroundColor Yellow
    }
    
    # Try to remove the directory completely
    Write-Host "4. Removing .next directory for clean start..." -ForegroundColor Yellow
    try {
        Remove-Item "$nextPath" -Recurse -Force -ErrorAction Stop
        Write-Host "   ✅ Removed .next directory successfully" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Could not remove .next directory: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "3. No .next directory found (this is good!)" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Permission fix complete!" -ForegroundColor Green
Write-Host "Now you can run: cd transcription-outpost\web; npm run dev:http" -ForegroundColor Cyan 