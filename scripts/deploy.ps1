# Deployment script for Lead Intelligence Platform (PowerShell)
# Usage: .\scripts\deploy.ps1 [environment]
# Environment: dev, staging, prod

param(
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Write-Host "🚀 Starting deployment for environment: $Environment" -ForegroundColor Green
Write-Host "📁 Project directory: $ProjectDir" -ForegroundColor Cyan

Set-Location $ProjectDir

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed" -ForegroundColor Red
    exit 1
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "⚠️  Please edit .env file with your configuration before continuing" -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "❌ .env.example not found" -ForegroundColor Red
        exit 1
    }
}

# Build Docker images
Write-Host "🔨 Building Docker images..." -ForegroundColor Green
docker-compose -f docker-compose.prod.yml build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yml down

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Green
docker-compose -f docker-compose.prod.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check health
$MaxRetries = 30
$RetryCount = 0
$Healthy = $false

while ($RetryCount -lt $MaxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $Healthy = $true
            break
        }
    } catch {
        # Continue retrying
    }
    
    $RetryCount++
    Write-Host "⏳ Waiting for backend... ($RetryCount/$MaxRetries)" -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

if ($Healthy) {
    Write-Host "✅ Backend is healthy!" -ForegroundColor Green
    
    # Run database migrations
    Write-Host "📊 Running database migrations..." -ForegroundColor Yellow
    docker-compose -f docker-compose.prod.yml exec -T backend python -m backend.scripts.create_migrations 2>&1 | Out-Null
    
    # Show service status
    Write-Host "📊 Service status:" -ForegroundColor Green
    docker-compose -f docker-compose.prod.yml ps
    
    Write-Host "✅ Deployment complete!" -ForegroundColor Green
    Write-Host "🌐 Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
} else {
    Write-Host "❌ Backend failed to become healthy" -ForegroundColor Red
    Write-Host "📋 Checking logs..." -ForegroundColor Yellow
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
}

