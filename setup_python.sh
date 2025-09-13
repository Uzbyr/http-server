#!/bin/bash

echo "🐍 Setting up LeChat MCP Hackathon - Python Version"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.8+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
MISTRAL_API_KEY=9YlToHIyCLSV6XzijYjPmykbX62XC9CF
MISTRAL_BASE_URL=https://api.mistral.ai/v1
MCP_SERVER_PORT=3000
MCP_SERVER_NAME=lechat-game-mcp
GAME_PORT=3001
GAME_NAME=Hobbo Hotel
EOF
    echo "⚠️  .env file created with your Mistral API key"
else
    echo "✅ .env file already exists"
fi

# Make the MCP server executable
chmod +x src/mcp_server.py

echo ""
echo "🎉 Python setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the MCP server: python src/mcp_server.py"
echo "3. Add the MCP server to LeChat:"
echo "   - Server name: lechat-game-mcp"
echo "   - Command: python src/mcp_server.py"
echo "   - Working directory: $(pwd)"
echo "4. Test with: python test_mcp.py"
echo ""
echo "Happy hacking! 🚀"
