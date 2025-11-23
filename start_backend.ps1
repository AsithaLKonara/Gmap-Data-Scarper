# Start FastAPI Backend Server
Write-Host "Starting Lead Intelligence Platform Backend..." -ForegroundColor Green
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

