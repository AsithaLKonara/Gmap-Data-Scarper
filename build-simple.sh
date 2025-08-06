#!/bin/bash

echo "🐳 Building LeadTap with Docker (Simple Version)..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Stopping existing containers...${NC}"
docker-compose -f docker-compose-simple.yml down --remove-orphans

echo -e "${BLUE}🔨 Building images...${NC}"
docker-compose -f docker-compose-simple.yml build --no-cache

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed. Check the error messages above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Images built successfully!${NC}"

echo -e "${BLUE}🚀 Starting services...${NC}"
docker-compose -f docker-compose-simple.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start services.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Services started!${NC}"

# Wait for services
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 15

# Check health
echo -e "${BLUE}🔍 Checking service health...${NC}"

if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is healthy!${NC}"
else
    echo -e "${RED}❌ Frontend health check failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 LeadTap is now running!${NC}"
echo ""
echo "📱 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose -f docker-compose-simple.yml logs -f"
echo "   Stop: docker-compose -f docker-compose-simple.yml down"
echo "   Restart: docker-compose -f docker-compose-simple.yml restart"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}" 
 

echo "🐳 Building LeadTap with Docker (Simple Version)..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Stopping existing containers...${NC}"
docker-compose -f docker-compose-simple.yml down --remove-orphans

echo -e "${BLUE}🔨 Building images...${NC}"
docker-compose -f docker-compose-simple.yml build --no-cache

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed. Check the error messages above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Images built successfully!${NC}"

echo -e "${BLUE}🚀 Starting services...${NC}"
docker-compose -f docker-compose-simple.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start services.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Services started!${NC}"

# Wait for services
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 15

# Check health
echo -e "${BLUE}🔍 Checking service health...${NC}"

if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is healthy!${NC}"
else
    echo -e "${RED}❌ Frontend health check failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 LeadTap is now running!${NC}"
echo ""
echo "📱 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose -f docker-compose-simple.yml logs -f"
echo "   Stop: docker-compose -f docker-compose-simple.yml down"
echo "   Restart: docker-compose -f docker-compose-simple.yml restart"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}" 
 

echo "🐳 Building LeadTap with Docker (Simple Version)..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Stopping existing containers...${NC}"
docker-compose -f docker-compose-simple.yml down --remove-orphans

echo -e "${BLUE}🔨 Building images...${NC}"
docker-compose -f docker-compose-simple.yml build --no-cache

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed. Check the error messages above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Images built successfully!${NC}"

echo -e "${BLUE}🚀 Starting services...${NC}"
docker-compose -f docker-compose-simple.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start services.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Services started!${NC}"

# Wait for services
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 15

# Check health
echo -e "${BLUE}🔍 Checking service health...${NC}"

if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is healthy!${NC}"
else
    echo -e "${RED}❌ Frontend health check failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 LeadTap is now running!${NC}"
echo ""
echo "📱 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose -f docker-compose-simple.yml logs -f"
echo "   Stop: docker-compose -f docker-compose-simple.yml down"
echo "   Restart: docker-compose -f docker-compose-simple.yml restart"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}" 
 