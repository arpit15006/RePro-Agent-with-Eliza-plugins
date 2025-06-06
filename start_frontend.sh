#!/bin/bash
# Start RePRO-Agent Frontend Development Server

echo "🎨 Starting RePRO-Agent Frontend..."

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "   Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Create .env file for frontend if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating frontend environment file..."
    cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF
fi

# Start the development server
echo "🌐 Starting Vite development server..."
echo "🎨 Frontend will be available at http://localhost:5173"
echo "🔄 Hot reload enabled - changes will be reflected automatically"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

npm run dev
