# Start Both Backend and Frontend
Write-Host "Starting Lead Intelligence Platform..." -ForegroundColor Green
Write-Host ""

# Start backend in background
Write-Host "Starting Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting Frontend..." -ForegroundColor Yellow
Set-Location frontend
npm run dev

