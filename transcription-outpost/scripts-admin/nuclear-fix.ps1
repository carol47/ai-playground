#!/usr/bin/env pwsh

Write-Host "💥 Nuclear Fix for Next.js Permission Issues" -ForegroundColor Red
Write-Host "===========================================" -ForegroundColor Red

# Kill all Node processes
Write-Host "1. Terminating all Node.js processes..." -ForegroundColor Yellow
taskkill /F /IM node.exe 2>$null
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force

# Navigate to project
$webPath = "C:\Users\carol\code\ai-playground\transcription-outpost\web"
Set-Location $webPath

Write-Host "2. Working in: $webPath" -ForegroundColor Yellow

# Multiple approaches to remove .next directory
$nextPath = Join-Path $webPath ".next"
if (Test-Path $nextPath) {
    Write-Host "3. Found problematic .next directory, attempting nuclear removal..." -ForegroundColor Yellow
    
    # Method 1: Take ownership
    Write-Host "   - Taking ownership..." -ForegroundColor Cyan
    takeown /F "$nextPath" /R /D Y 2>$null
    
    # Method 2: Grant permissions  
    Write-Host "   - Granting permissions..." -ForegroundColor Cyan
    icacls "$nextPath" /grant "$env:USERNAME:(F)" /T /Q 2>$null
    icacls "$nextPath" /grant "Everyone:(F)" /T /Q 2>$null
    
    # Method 3: Remove read-only attributes
    Write-Host "   - Removing read-only attributes..." -ForegroundColor Cyan
    attrib -R "$nextPath\*" /S /D 2>$null
    
    # Method 4: Force remove with multiple attempts
    for ($i = 1; $i -le 3; $i++) {
        Write-Host "   - Removal attempt $i..." -ForegroundColor Cyan
        try {
            Remove-Item "$nextPath" -Recurse -Force -ErrorAction Stop
            Write-Host "   ✅ Successfully removed .next directory!" -ForegroundColor Green
            break
        } catch {
            Write-Host "   ⚠️  Attempt $i failed: $($_.Exception.Message)" -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
    }
    
    # Method 5: CMD fallback
    if (Test-Path $nextPath) {
        Write-Host "   - Using CMD as last resort..." -ForegroundColor Cyan
        cmd /c "rmdir /s /q `"$nextPath`"" 2>$null
    }
    
    # Method 6: Move instead of delete
    if (Test-Path $nextPath) {
        Write-Host "   - Moving directory to temp location..." -ForegroundColor Cyan
        $tempPath = Join-Path $env:TEMP "next-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        try {
            Move-Item "$nextPath" "$tempPath" -Force
            Write-Host "   ✅ Moved to: $tempPath" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ Move failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "3. No .next directory found (good!)" -ForegroundColor Green
}

# Clear npm cache aggressively
Write-Host "4. Clearing npm cache..." -ForegroundColor Yellow
npm cache clean --force 2>$null

# Try to start the server
Write-Host "5. Starting HTTPS server..." -ForegroundColor Yellow
Write-Host "   Command: `$env:FASTAPI_URL='http://192.168.0.76:8000'; node server.js" -ForegroundColor Cyan

$env:FASTAPI_URL = "http://192.168.0.76:8000"
try {
    Write-Host "🚀 Starting server..." -ForegroundColor Green
    node server.js
} catch {
    Write-Host "❌ Server failed to start: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Try running manually: cd transcription-outpost\web; `$env:FASTAPI_URL='http://192.168.0.76:8000'; node server.js" -ForegroundColor Yellow
} 