 

echo "🐳 Building LeadTap Backend Only..."

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
docker-compose -f docker-compose-backend-only.yml down --remove-orphans

echo -e "${BLUE}🔨 Building backend image...${NC}"
docker-compose -f docker-compose-backend-only.yml build --no-cache

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Backend build failed. Check the error messages above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend image built successfully!${NC}"

echo -e "${BLUE}🚀 Starting backend service...${NC}"
docker-compose -f docker-compose-backend-only.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start backend service.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend service started!${NC}"

# Wait for service
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
sleep 10

# Check health
echo -e "${BLUE}🔍 Checking backend health...${NC}"

if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
    echo ""
    echo -e "${GREEN}🎉 LeadTap Backend is running!${NC}"
    echo ""
    echo "📱 Access your backend:"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo "   Health Check: http://localhost:8000/api/health"
    echo ""
    echo "🔧 Useful commands:"
    echo "   View logs: docker-compose -f docker-compose-backend-only.yml logs -f"
    echo "   Stop: docker-compose -f docker-compose-backend-only.yml down"
    echo "   Restart: docker-compose -f docker-compose-backend-only.yml restart"
    echo ""
    echo -e "${GREEN}Backend is ready! 🚀${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo -e "${BLUE}📋 Checking logs...${NC}"
    docker-compose -f docker-compose-backend-only.yml logs backend
fi 
 

echo "🐳 Building LeadTap Backend Only..."

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
docker-compose -f docker-compose-backend-only.yml down --remove-orphans

echo -e "${BLUE}🔨 Building backend image...${NC}"
docker-compose -f docker-compose-backend-only.yml build --no-cache

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Backend build failed. Check the error messages above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend image built successfully!${NC}"

echo -e "${BLUE}🚀 Starting backend service...${NC}"
docker-compose -f docker-compose-backend-only.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start backend service.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend service started!${NC}"

# Wait for service
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
sleep 10

# Check health
echo -e "${BLUE}🔍 Checking backend health...${NC}"

if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
    echo ""
    echo -e "${GREEN}🎉 LeadTap Backend is running!${NC}"
    echo ""
    echo "📱 Access your backend:"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo "   Health Check: http://localhost:8000/api/health"
    echo ""
    echo "🔧 Useful commands:"
    echo "   View logs: docker-compose -f docker-compose-backend-only.yml logs -f"
    echo "   Stop: docker-compose -f docker-compose-backend-only.yml down"
    echo "   Restart: docker-compose -f docker-compose-backend-only.yml restart"
    echo ""
    echo -e "${GREEN}Backend is ready! 🚀${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo -e "${BLUE}📋 Checking logs...${NC}"
    docker-compose -f docker-compose-backend-only.yml logs backend
fi 
 

echo "🐳 Building LeadTap Backend Only..."

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
docker-compose -f docker-compose-backend-only.yml down --remove-orphans

echo -e "${BLUE}🔨 Building backend image...${NC}"
docker-compose -f docker-compose-backend-only.yml build --no-cache

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Backend build failed. Check the error messages above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend image built successfully!${NC}"

echo -e "${BLUE}🚀 Starting backend service...${NC}"
docker-compose -f docker-compose-backend-only.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start backend service.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend service started!${NC}"

# Wait for service
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
sleep 10

# Check health
echo -e "${BLUE}🔍 Checking backend health...${NC}"

if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
    echo ""
    echo -e "${GREEN}🎉 LeadTap Backend is running!${NC}"
    echo ""
    echo "📱 Access your backend:"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo "   Health Check: http://localhost:8000/api/health"
    echo ""
    echo "🔧 Useful commands:"
    echo "   View logs: docker-compose -f docker-compose-backend-only.yml logs -f"
    echo "   Stop: docker-compose -f docker-compose-backend-only.yml down"
    echo "   Restart: docker-compose -f docker-compose-backend-only.yml restart"
    echo ""
    echo -e "${GREEN}Backend is ready! 🚀${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo -e "${BLUE}📋 Checking logs...${NC}"
    docker-compose -f docker-compose-backend-only.yml logs backend
fi 
 