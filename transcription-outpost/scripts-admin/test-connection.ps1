#!/usr/bin/env pwsh

Write-Host "🔍 Testing Transcription Service Connection" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Test backend directly
Write-Host "1. Testing Backend API..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://192.168.0.76:8000/health" -Method Get -TimeoutSec 5
    Write-Host "   ✅ Backend is responding: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend not responding: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test frontend
Write-Host "2. Testing Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://192.168.0.76:3001" -SkipCertificateCheck -TimeoutSec 5
    Write-Host "   ✅ Frontend HTTPS is responding (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Frontend not responding: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test API endpoint
Write-Host "3. Testing API Endpoint..." -ForegroundColor Yellow
try {
    # Create a simple test file
    $testContent = "Hello, this is a test audio file."
    $testBytes = [System.Text.Encoding]::UTF8.GetBytes($testContent)
    $boundary = "----WebKitFormBoundary" + [System.Guid]::NewGuid().ToString("N")
    
    $body = @"
--$boundary
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

$testContent
--$boundary--
"@
    
    $headers = @{
        "Content-Type" = "multipart/form-data; boundary=$boundary"
    }
    
    $response = Invoke-RestMethod -Uri "https://192.168.0.76:3001/api/transcribe" -Method Post -Body $body -Headers $headers -SkipCertificateCheck -TimeoutSec 10
    Write-Host "   ✅ API endpoint responding: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ API endpoint error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "   📄 Response status: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎯 Quick Fix Commands:" -ForegroundColor Cyan
Write-Host "- Backend: cd transcription-outpost; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host "- Frontend: cd transcription-outpost\web; `$env:FASTAPI_URL='http://192.168.0.76:8000'; node server.js" -ForegroundColor White 