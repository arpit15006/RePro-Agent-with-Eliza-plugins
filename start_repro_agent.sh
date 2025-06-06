#!/bin/bash
# Start Complete RePRO-Agent Application (Backend + Frontend)

echo "🧬 RePRO-Agent - Scientific Reproducibility & Hypothesis Generation"
echo "=================================================================="
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    if port_in_use $1; then
        echo "🔄 Killing existing process on port $1..."
        lsof -ti :$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8+ from https://python.org/"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    echo "   Please install Node.js from https://nodejs.org/"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed."
    exit 1
fi

echo "✅ All prerequisites found"
echo ""

# Setup environment
echo "⚙️ Setting up environment..."

# Load environment variables
if [ -f ".env" ]; then
    echo "📄 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Using default configuration."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
cd backend && pip install -q -r requirements.txt && cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/temp_uploads
mkdir -p backend/temp_graphs  
mkdir -p backend/temp_downloads
mkdir -p backend/analysis_results
mkdir -p output

echo "✅ Environment setup complete"
echo ""

# Kill existing processes on our ports
kill_port 8000
kill_port 5173

# Start backend server
echo "🚀 Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if ! port_in_use 8000; then
    echo "❌ Backend failed to start on port 8000"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend server running on http://localhost:8000"

# Start frontend server
echo "🎨 Starting frontend server..."
cd frontend

# Create frontend .env if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF
fi

npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 8

# Check if frontend is running
if ! port_in_use 5173; then
    echo "❌ Frontend failed to start on port 5173"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Frontend server running on http://localhost:5173"
echo ""

# Display success message
echo "🎉 RePRO-Agent is now running!"
echo "================================"
echo ""
echo "🌐 Frontend:  http://localhost:5173"
echo "🔧 Backend:   http://localhost:8000"
echo "📖 API Docs:  http://localhost:8000/docs"
echo ""
echo "🧬 Features Available:"
echo "  • Upload and analyze scientific papers"
echo "  • Assess repository reproducibility"
echo "  • Build interactive knowledge graphs"
echo "  • Generate AI-powered research hypotheses"
echo ""
echo "🔑 API Key Configuration:"
echo "  • Your Gemini API key is already configured"
echo "  • Add OpenAI/Anthropic keys in Settings for additional models"
echo ""
echo "🛑 To stop the servers, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down RePRO-Agent..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Keep script running and show logs
echo "📊 Server Status (press Ctrl+C to stop):"
echo "----------------------------------------"

# Wait for user to stop
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend process died unexpectedly"
        break
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend process died unexpectedly"
        break
    fi
    
    sleep 5
done

cleanup
