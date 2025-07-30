#!/bin/bash

# FastAPI Backend Setup Script
echo "🔧 Setting up FastAPI Backend..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from template
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "🔧 Please edit .env file and add your OPENROUTER_API_KEY"
else
    echo "✅ .env file already exists"
fi

# Make start script executable
chmod +x start.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OPENROUTER_API_KEY"
echo "2. Run ./start.sh to start the server"
echo "3. Visit http://localhost:8081/docs for API documentation"