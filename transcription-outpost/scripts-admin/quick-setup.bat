@echo off
echo.
echo 🔧 Setting up Transcription Outpost for Network Access...
echo.

echo 📡 Finding your network IP addresses...
echo.
ipconfig | findstr /C:"IPv4 Address"

echo.
echo 🔥 Adding Windows Firewall rules...
echo.
netsh advfirewall firewall add rule name="Transcription Backend (Port 8000)" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1
netsh advfirewall firewall add rule name="Transcription Frontend HTTPS (Port 3001)" dir=in action=allow protocol=TCP localport=3001 >nul 2>&1
netsh advfirewall firewall add rule name="Transcription Frontend HTTP (Port 3002)" dir=in action=allow protocol=TCP localport=3002 >nul 2>&1

if %errorlevel% == 0 (
    echo ✅ Firewall rules added successfully!
) else (
    echo ⚠️ Could not add firewall rules. You might need to run as Administrator.
)

echo.
echo 🚀 Starting HTTP version of frontend...
echo.
start "Frontend HTTP Server" cmd /k "cd /d %~dp0web && npm run dev:http"

echo.
echo 🎯 Your services are now accessible from other computers!
echo.
echo Use YOUR LOCAL IP ADDRESS (not 10.5.0.2) from the list above:
echo.
echo Example: If your IP is 192.168.1.100, use:
echo   • Frontend HTTP:  http://192.168.1.100:3002
echo   • Frontend HTTPS: https://192.168.1.100:3001  
echo   • Backend API:    http://192.168.1.100:8000
echo.
echo ✨ The HTTP version (port 3002) is easier for testing!
echo.
pause 