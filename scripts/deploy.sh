#!/bin/bash
# Deployment script for Lead Intelligence Platform
# Usage: ./scripts/deploy.sh [environment]
# Environment: dev, staging, prod

set -e

ENVIRONMENT=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting deployment for environment: $ENVIRONMENT"
echo "📁 Project directory: $PROJECT_DIR"

cd "$PROJECT_DIR"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env file with your configuration before continuing${NC}"
        exit 1
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        exit 1
    fi
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Build Docker images
echo -e "${GREEN}🔨 Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Start services
echo -e "${GREEN}🚀 Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check health
MAX_RETRIES=30
RETRY_COUNT=0
HEALTHY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        HEALTHY=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}⏳ Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ "$HEALTHY" = true ]; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
    
    # Run database migrations
    echo -e "${YELLOW}📊 Running database migrations...${NC}"
    docker-compose -f docker-compose.prod.yml exec -T backend python -m backend.scripts.create_migrations || true
    
    # Show service status
    echo -e "${GREEN}📊 Service status:${NC}"
    docker-compose -f docker-compose.prod.yml ps
    
    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo -e "${GREEN}🌐 Backend API: http://localhost:8000${NC}"
    echo -e "${GREEN}📚 API Docs: http://localhost:8000/docs${NC}"
else
    echo -e "${RED}❌ Backend failed to become healthy${NC}"
    echo -e "${YELLOW}📋 Checking logs...${NC}"
    docker-compose -f docker-compose.prod.yml logs backend
    exit 1
fi

