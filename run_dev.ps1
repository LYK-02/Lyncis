# Lyncis Development Runner (PowerShell)
Write-Host "========================================" -ForegroundColor Green
Write-Host "Starting Lyncis OSINT Platform Services" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 1. Start Python API in Background
$env:PYTHONPATH = "apps/api"
$apiProcess = Start-Process python -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000" -PassThru -NoNewWindow
Write-Host "[+] Lyncis API started on http://127.0.0.1:8000 (PID: $($apiProcess.Id))" -ForegroundColor Cyan

# 2. Start Next.js Web
Set-Location apps/web
Write-Host "[+] Starting Next.js Web console on http://localhost:3000..." -ForegroundColor Cyan
pnpm dev
