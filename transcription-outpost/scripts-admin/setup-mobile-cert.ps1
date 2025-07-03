#!/usr/bin/env pwsh

Write-Host "🔐 Mobile Certificate Setup Helper" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if HTTPS service is running
$httpsRunning = netstat -an | Select-String ":3001" | Select-String "LISTENING"
if ($httpsRunning) {
    Write-Host "✅ HTTPS service is running on port 3001" -ForegroundColor Green
} else {
    Write-Host "❌ HTTPS service is not running. Start it with: npm run dev:https" -ForegroundColor Red
    Write-Host ""
}

# Check if certificate files exist
$certPath = "web\certs\cert.pem"
$keyPath = "web\certs\key.pem"

if (Test-Path $certPath) {
    Write-Host "✅ Certificate file found: $certPath" -ForegroundColor Green
} else {
    Write-Host "❌ Certificate file not found: $certPath" -ForegroundColor Red
}

if (Test-Path $keyPath) {
    Write-Host "✅ Key file found: $keyPath" -ForegroundColor Green
} else {
    Write-Host "❌ Key file not found: $keyPath" -ForegroundColor Red
}

Write-Host ""
Write-Host "🌐 Your service URLs:" -ForegroundColor Yellow
Write-Host "   Local (this computer): https://localhost:3001" -ForegroundColor White
Write-Host "   Network (other devices): https://192.168.0.76:3001" -ForegroundColor White
Write-Host ""

Write-Host "📱 To add certificate to your mobile device:" -ForegroundColor Yellow
Write-Host "   1. On your mobile device, navigate to: https://192.168.0.76:3001" -ForegroundColor White
Write-Host "   2. Your browser will show a security warning" -ForegroundColor White
Write-Host "   3. Tap 'Advanced' or 'More details'" -ForegroundColor White
Write-Host "   4. Tap 'Add Exception' or 'Proceed to site'" -ForegroundColor White
Write-Host "   5. For permanent trust, save the certificate to your device" -ForegroundColor White
Write-Host ""

Write-Host "🔧 Alternative certificate download:" -ForegroundColor Yellow
Write-Host "   You can download the certificate directly from:" -ForegroundColor White
Write-Host "   http://192.168.0.76:3002/cert.pem (if HTTP service is also running)" -ForegroundColor White
Write-Host ""

Write-Host "💡 Pro tip: Once you accept the certificate, microphone access will work!" -ForegroundColor Cyan 