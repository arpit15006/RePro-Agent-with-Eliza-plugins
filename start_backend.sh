#!/bin/bash
# Start RePRO-Agent Backend Server

echo "🚀 Starting RePRO-Agent Backend Server..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📚 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Install main project dependencies
echo "📚 Installing main project dependencies..."
cd ..
pip install -r requirements.txt

# Set environment variables
if [ -f ".env" ]; then
    echo "⚙️ Loading environment variables..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/temp_uploads
mkdir -p backend/temp_graphs
mkdir -p backend/temp_downloads
mkdir -p backend/analysis_results

# Start the backend server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📖 API documentation available at http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

cd backend
python main.py
