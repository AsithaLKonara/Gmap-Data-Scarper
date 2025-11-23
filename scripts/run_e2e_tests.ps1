# Comprehensive E2E test runner for Windows PowerShell
# This script runs all E2E tests and generates a detailed report

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Lead Intelligence Platform - E2E Tests" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
Write-Host "Checking backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend is not running on port 8000" -ForegroundColor Yellow
    Write-Host "   Please start it with: python backend/main.py" -ForegroundColor Yellow
}

# Check if frontend is running
Write-Host "Checking frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Frontend is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Frontend is not running on port 3000" -ForegroundColor Yellow
    Write-Host "   Please start it with: cd frontend; npm run dev" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Running E2E tests..." -ForegroundColor Yellow
Write-Host ""

Set-Location frontend
npx playwright test --reporter=html --reporter=list

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Test Results Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "View detailed report: frontend/playwright-report/index.html" -ForegroundColor Green
Write-Host ""

