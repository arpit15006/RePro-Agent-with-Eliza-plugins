#!/bin/bash
# RePRO-Agent Installation Script
# Scientific Reproducibility and Hypothesis Generation Pipeline

set -e  # Exit on any error

echo "🧬 RePRO-Agent Installation Script"
echo "=================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python 3.8+ is available
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.8 or higher is required"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install main requirements
echo "📚 Installing main requirements..."
pip install -r requirements.txt

# Install individual plugin requirements
echo "🔧 Installing plugin-specific requirements..."

plugins=("manuscript-extractor" "reproducibility-assistant" "knowledge-graph-builder" "hypothesis-generator")

for plugin in "${plugins[@]}"; do
    if [ -f "$plugin/requirements.txt" ]; then
        echo "  Installing $plugin requirements..."
        pip install -r "$plugin/requirements.txt"
    fi
done

# Install development dependencies (optional)
read -p "📝 Install development dependencies? (y/N): " install_dev
if [[ $install_dev =~ ^[Yy]$ ]]; then
    echo "🛠️ Installing development dependencies..."
    pip install pytest pytest-cov black flake8 mypy sphinx sphinx-rtd-theme
fi

# Check Docker availability (optional but recommended)
echo "🐳 Checking Docker availability..."
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        echo "✅ Docker is available and running"
    else
        echo "⚠️ Docker is installed but not running"
        echo "   Start Docker to enable full reproducibility assessment features"
    fi
else
    echo "⚠️ Docker not found"
    echo "   Install Docker to enable containerized reproducibility testing"
    echo "   Visit: https://docs.docker.com/get-docker/"
fi

# Create example environment file
echo "⚙️ Creating example environment file..."
cat > .env.example << 'EOF'
# API Keys for LLM services (choose one or both)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: SPARQL endpoint for remote graph storage
SPARQL_ENDPOINT=http://localhost:3030/dataset

# Optional: Docker host (if using remote Docker)
DOCKER_HOST=unix:///var/run/docker.sock
EOF

echo "✅ Example environment file created: .env.example"
echo "   Copy this to .env and add your API keys"

# Create output directory
echo "📁 Creating output directory..."
mkdir -p output
echo "✅ Output directory created"

# Run basic tests
echo "🧪 Running basic installation tests..."

# Test each plugin
for plugin in "${plugins[@]}"; do
    echo "  Testing $plugin..."
    if python3 "$plugin/main.py" --help &> /dev/null; then
        echo "    ✅ $plugin OK"
    else
        echo "    ❌ $plugin failed"
    fi
done

# Test main pipeline
echo "  Testing main pipeline..."
if python3 pipeline.py --help &> /dev/null; then
    echo "    ✅ Main pipeline OK"
else
    echo "    ❌ Main pipeline failed"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Copy .env.example to .env and add your API keys:"
echo "   cp .env.example .env"
echo "   # Edit .env with your favorite editor"
echo ""
echo "2. Test the pipeline with a sample paper:"
echo "   python3 pipeline.py --paper sample_paper.pdf --repo https://github.com/user/repo"
echo ""
echo "3. Or run individual plugins:"
echo "   python3 manuscript-extractor/main.py --input paper.pdf"
echo "   python3 reproducibility-assistant/main.py --repo https://github.com/user/repo"
echo ""
echo "📖 For more information, see README.md"
echo "🐛 Report issues at: https://github.com/yourusername/eliza-repro-hypothesis/issues"
echo ""
echo "Happy researching! 🧬✨"
