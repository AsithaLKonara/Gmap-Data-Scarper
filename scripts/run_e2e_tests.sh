#!/bin/bash
# Comprehensive E2E test runner
# This script runs all E2E tests and generates a detailed report

echo "=========================================="
echo "Lead Intelligence Platform - E2E Tests"
echo "=========================================="
echo ""

# Check if backend is running
echo "Checking backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend is not running on port 8000"
    echo "   Starting backend..."
    # Start backend in background (adjust command as needed)
    # python backend/main.py &
fi

# Check if frontend is running
echo "Checking frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend is not running on port 3000"
    echo "   Please start it with: cd frontend && npm run dev"
    exit 1
fi

echo ""
echo "Running E2E tests..."
echo ""

cd frontend
npx playwright test --reporter=html --reporter=list

echo ""
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo "View detailed report: frontend/playwright-report/index.html"
echo ""

