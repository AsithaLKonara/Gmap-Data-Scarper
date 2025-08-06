#!/bin/bash

# Start the development servers for the GMap Data Scraper project

echo "🚀 Starting GMap Data Scraper Development Environment..."

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Shutting down development servers..."
    kill $FRONTEND_PID $BACKEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting backend server..."
cd backend
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "🌐 Starting backend on http://localhost:8000"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd ../frontend
echo "📦 Installing frontend dependencies..."
npm install > /dev/null 2>&1

echo "🌐 Starting frontend on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development servers started!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait 
 

# Start the development servers for the GMap Data Scraper project

echo "🚀 Starting GMap Data Scraper Development Environment..."

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Shutting down development servers..."
    kill $FRONTEND_PID $BACKEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting backend server..."
cd backend
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "🌐 Starting backend on http://localhost:8000"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd ../frontend
echo "📦 Installing frontend dependencies..."
npm install > /dev/null 2>&1

echo "🌐 Starting frontend on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development servers started!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait 
 

# Start the development servers for the GMap Data Scraper project

echo "🚀 Starting GMap Data Scraper Development Environment..."

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Shutting down development servers..."
    kill $FRONTEND_PID $BACKEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting backend server..."
cd backend
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "🌐 Starting backend on http://localhost:8000"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd ../frontend
echo "📦 Installing frontend dependencies..."
npm install > /dev/null 2>&1

echo "🌐 Starting frontend on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Development servers started!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait 
 