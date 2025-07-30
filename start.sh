#!/bin/bash

# FastAPI Backend Start Script
echo "🚀 Starting FastAPI Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/pyvenv.cfg" ] || ! pip show fastapi > /dev/null 2>&1; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "🔧 Please edit .env file and add your OPENROUTER_API_KEY"
fi

# Start the server
echo "🌟 Starting FastAPI server on http://0.0.0.0:8081"
echo "📚 API docs available at http://localhost:8081/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

uvicorn fastapi_backend.main:app --host 0.0.0.0 --port 8081 --reload