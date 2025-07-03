#!/usr/bin/env pwsh

Write-Host "🔐 Setting up Next.js HTTPS with mkcert" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if mkcert is installed
Write-Host "1. Checking for mkcert..." -ForegroundColor Yellow
$mkcertExists = Get-Command mkcert -ErrorAction SilentlyContinue
if (-not $mkcertExists) {
    Write-Host "   ❌ mkcert not found. Installing via Chocolatey..." -ForegroundColor Red
    
    # Check if Chocolatey is installed
    $chocoExists = Get-Command choco -ErrorAction SilentlyContinue
    if (-not $chocoExists) {
        Write-Host "   📦 Installing Chocolatey first..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    
    Write-Host "   📦 Installing mkcert..." -ForegroundColor Yellow
    choco install mkcert -y
    
    # Refresh environment variables again
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "   ✅ mkcert found!" -ForegroundColor Green
}

# Install the local CA
Write-Host "2. Installing local Certificate Authority..." -ForegroundColor Yellow
try {
    mkcert -install
    Write-Host "   ✅ Local CA installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  CA installation may have failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Create certificates for localhost and local IP
Write-Host "3. Creating certificates..." -ForegroundColor Yellow
$webDir = "web"
if (-not (Test-Path $webDir)) {
    New-Item -ItemType Directory -Path $webDir
}

Set-Location $webDir

try {
    # Next.js --experimental-https looks for these specific filenames
    mkcert localhost 192.168.0.76
    Write-Host "   ✅ Certificates created successfully!" -ForegroundColor Green
    Write-Host "   📄 Files created: localhost.pem, localhost-key.pem" -ForegroundColor Blue
} catch {
    Write-Host "   ❌ Certificate creation failed: $($_.Exception.Message)" -ForegroundColor Red
}

Set-Location ..

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 To start your HTTPS server:" -ForegroundColor Cyan
Write-Host "   cd web" -ForegroundColor White
Write-Host "   npm run dev:https" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Your app will be available at:" -ForegroundColor Cyan
Write-Host "   https://localhost:3001 (local)" -ForegroundColor White
Write-Host "   https://192.168.0.76:3001 (network)" -ForegroundColor White
Write-Host ""
Write-Host "📱 For mobile access:" -ForegroundColor Yellow
Write-Host "   1. Navigate to https://192.168.0.76:3001 on your phone" -ForegroundColor White
Write-Host "   2. Accept the security warning" -ForegroundColor White
Write-Host "   3. Your microphone will work perfectly! 🎤" -ForegroundColor White 