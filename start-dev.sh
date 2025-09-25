#!/bin/bash

# Kochi Metro Trainset Induction Planner - Development Starter
# For Mac/Linux systems

echo "============================================================"
echo "🚀 Kochi Metro Trainset Induction Planner - Dev Starter"
echo "============================================================"

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo
echo "📂 Working directory: $SCRIPT_DIR"

echo
echo "🔍 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
else
    echo "✅ Python 3 is available"
fi

if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/NPM is not installed"
    exit 1
else
    echo "✅ Node.js/NPM is available"
fi

# Function to start backend
start_backend() {
    echo
    echo "🔧 Starting Backend Server..."
    
    if [ ! -d "backend" ]; then
        echo "❌ Backend directory not found"
        return 1
    fi
    
    cd backend
    # Start backend in background
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload > backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    echo "✅ Backend server started (PID: $BACKEND_PID) - logs in backend.log"
    return 0
}

# Function to start frontend
start_frontend() {
    echo
    echo "🌐 Starting Frontend Server..."
    
    if [ ! -d "frontend" ]; then
        echo "❌ Frontend directory not found"
        return 1
    fi
    
    cd frontend
    # Start frontend in background
    npm start > frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Frontend server started (PID: $FRONTEND_PID) - logs in frontend.log"
    return 0
}

# Function to stop servers
stop_servers() {
    echo
    echo "🛑 Stopping servers..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend server stopped"
    fi
    
    exit 0
}

# Set up signal handlers
trap stop_servers SIGINT SIGTERM

# Start the servers
if start_backend && start_frontend; then
    echo
    echo "============================================================"
    echo "✨ Both servers are now running!"
    echo "   Backend:  http://localhost:8001"
    echo "   Frontend: http://localhost:3000"
    echo
    echo "📝 Keep this terminal open while developing"
    echo "   Press Ctrl+C to stop both servers"
    echo "============================================================"
    
    # Wait for processes
    wait
else
    echo
    echo "❌ Failed to start one or more servers"
    stop_servers
    exit 1
fi