#!/bin/bash

# LeadTap Docker Build and Run Script
echo "🐳 Building and running LeadTap with Docker..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running. Starting build process..."

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans

# Build the images
print_status "Building Docker images..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    print_error "Failed to build Docker images. Please check the error messages above."
    exit 1
fi

print_success "Docker images built successfully!"

# Start the services
print_status "Starting services..."
docker-compose up -d

if [ $? -ne 0 ]; then
    print_error "Failed to start services. Please check the error messages above."
    exit 1
fi

print_success "Services started successfully!"

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check backend
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    print_success "Backend is healthy!"
else
    print_warning "Backend health check failed. It may still be starting up..."
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend is healthy!"
else
    print_warning "Frontend health check failed. It may still be starting up..."
fi

# Show service status
print_status "Service status:"
docker-compose ps

# Show logs
print_status "Recent logs:"
docker-compose logs --tail=20

print_success "🎉 LeadTap is now running with Docker!"
echo ""
echo "📱 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Rebuild: docker-compose build --no-cache"
echo ""
print_success "Happy coding! 🚀" 
 