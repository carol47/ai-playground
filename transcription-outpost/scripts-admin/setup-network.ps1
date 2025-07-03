#!/usr/bin/env pwsh
# Network Setup Script for Transcription Outpost

Write-Host "🔧 Setting up network access for Transcription Outpost..." -ForegroundColor Green

# Show current IP addresses
Write-Host "`n📡 Current Network Configuration:" -ForegroundColor Yellow
ipconfig | Where-Object { $_ -match "IPv4 Address" -or $_ -match "Adapter" }

# Add Windows Firewall rules
Write-Host "`n🔥 Adding Windows Firewall rules..." -ForegroundColor Yellow

try {
    New-NetFirewallRule -DisplayName "Transcription Backend (Port 8000)" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "Transcription Frontend HTTPS (Port 3001)" -Direction Inbound -Protocol TCP -LocalPort 3001 -Action Allow -ErrorAction SilentlyContinue
    New-NetFirewallRule -DisplayName "Transcription Frontend HTTP (Port 3002)" -Direction Inbound -Protocol TCP -LocalPort 3002 -Action Allow -ErrorAction SilentlyContinue
    Write-Host "✅ Firewall rules added successfully!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not add firewall rules. You might need to run as Administrator." -ForegroundColor Red
}

# Show listening ports
Write-Host "`n🌐 Current listening ports:" -ForegroundColor Yellow
Get-NetTCPConnection | Where-Object {$_.State -eq "Listen" -and ($_.LocalPort -eq 8000 -or $_.LocalPort -eq 3001 -or $_.LocalPort -eq 3002)} | Format-Table LocalAddress,LocalPort,State

Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Find your local network IP address from the list above (usually starts with 192.168.x.x or 172.x.x.x)"
Write-Host "2. Use that IP instead of 10.5.0.2 (which is your VPN IP)"
Write-Host "3. Test HTTP version first: http://[YOUR_LOCAL_IP]:3002"
Write-Host "4. Then try HTTPS version: https://[YOUR_LOCAL_IP]:3001"
Write-Host ""
Write-Host "Example: If your local IP is 192.168.1.100, try:"
Write-Host "  • http://192.168.1.100:3002 (HTTP version)"
Write-Host "  • https://192.168.1.100:3001 (HTTPS version)" 