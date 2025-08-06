#!/bin/bash

# LeadTap Docker Build Script
echo "🚀 Building LeadTap with Docker..."

# Set environment variables
export SECRET_KEY="your-super-secret-key-change-this-in-production"
export NODE_ENV="production"

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Remove old images (optional)
echo "🧹 Cleaning up old images..."
docker system prune -f

# Build the images
echo "🔨 Building Docker images..."
docker-compose build --no-cache

# Start the services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Test the services
echo "🧪 Testing services..."
echo "Testing Backend API..."
curl -f http://localhost:8000/docs > /dev/null 2>&1 && echo "✅ Backend API is running" || echo "❌ Backend API failed"

echo "Testing Frontend..."
curl -f http://localhost:3000 > /dev/null 2>&1 && echo "✅ Frontend is running" || echo "❌ Frontend failed"

echo ""
echo "🎉 LeadTap is now running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down" 