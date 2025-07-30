@echo off

REM FastAPI Backend Start Script for Windows
echo 🚀 Starting FastAPI Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate

REM Check if dependencies are installed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Copying from .env.example...
    copy .env.example .env
    echo 🔧 Please edit .env file and add your OPENROUTER_API_KEY
)

REM Start the server
echo 🌟 Starting FastAPI server on http://0.0.0.0:8081
echo 📚 API docs available at http://localhost:8081/docs
echo 🛑 Press Ctrl+C to stop the server
echo.

uvicorn fastapi_backend.main:app --host 0.0.0.0 --port 8081 --reload