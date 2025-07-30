# FastAPI Backend with OpenRouter Integration

A FastAPI application with OpenRouter AI/LLM integration using LangChain.
<img width="921" height="664" alt="Screenshot 2025-07-30 at 9 34 48 AM" src="https://github.com/user-attachments/assets/13e873d6-0eca-48ae-b8e6-d7e22a136433" />

## Features

- FastAPI web framework with async support
- OpenRouter integration for multiple AI models
- LangChain for LLM operations
- Environment-based configuration
- Hot reload for development
- Health check endpoint
- Chat API with multiple model support

## Project Structure

```
fastapi-project/
├── fastapi_backend/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application and endpoints
│   └── openrouter.py        # OpenRouter integration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── venv/                   # Virtual environment (created during setup)
```

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
# If you haven't already, navigate to your project directory
cd your-project-directory
```

### 2. Create and Activate Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 langchain==0.3.20 langchain_openai==0.3.7 python-dotenv==1.0.0 pydantic==2.5.0
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` file and add your OpenRouter API key:
```bash
OPENROUTER_API_KEY=your_actual_openrouter_api_key_here
```

Get your API key from [OpenRouter](https://openrouter.ai/).

## Running the Application

### Start the Development Server

```bash
uvicorn fastapi_backend.main:app --host 0.0.0.0 --port 8081 --reload
```

The application will be available at:
- **API**: http://localhost:8081
- **Interactive API docs**: http://localhost:8081/docs
- **Alternative docs**: http://localhost:8081/redoc

### Quick Start Script

For convenience, you can create a start script:

**start.sh (macOS/Linux):**
```bash
#!/bin/bash
source venv/bin/activate
uvicorn fastapi_backend.main:app --host 0.0.0.0 --port 8081 --reload
```

**start.bat (Windows):**
```batch
@echo off
call venv\Scripts\activate
uvicorn fastapi_backend.main:app --host 0.0.0.0 --port 8081 --reload
```

Make it executable and run:
```bash
chmod +x start.sh
./start.sh
```

## API Endpoints

### Basic Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `GET /models` - List available OpenRouter models

### Chat Endpoint

- `POST /chat` - Chat with AI models

**Request body:**
```json
{
  "message": "Hello, how are you?",
  "model": "anthropic/claude-3.5-sonnet"
}
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking...",
  "model": "anthropic/claude-3.5-sonnet"
}
```

### Example Usage with curl

```bash
# Health check
curl http://localhost:8081/health

# Chat request
curl -X POST "http://localhost:8081/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is FastAPI?", "model": "anthropic/claude-3.5-sonnet"}'

# List models
curl http://localhost:8081/models
```

## Available Models

Popular OpenRouter models you can use:

- `anthropic/claude-3.5-sonnet` (default)
- `anthropic/claude-3-haiku`
- `openai/gpt-4-turbo`
- `openai/gpt-3.5-turbo`
- `meta-llama/llama-3.1-8b-instruct`
- `google/gemini-pro`

## Development

### Virtual Environment Management

**Activate virtual environment:**
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Deactivate virtual environment:**
```bash
deactivate
```

### Installing New Dependencies

```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install new package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt
```

## Troubleshooting

### Common Issues

**1. Virtual environment not found**
```bash
# Recreate virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Module not found errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**3. OpenRouter API key issues**
- Verify your API key is correct in `.env` file
- Check that `.env` file exists (copy from `.env.example`)
- Ensure no extra spaces around the API key

**4. Port already in use**
```bash
# Use a different port
uvicorn fastapi_backend.main:app --host 0.0.0.0 --port 8082 --reload
```

**5. Permission denied on macOS/Linux**
```bash
# Make start script executable
chmod +x start.sh
```

### Checking Setup

**Verify Python version:**
```bash
python3 --version  # Should be 3.8+
```

**Verify virtual environment:**
```bash
which python  # Should point to venv/bin/python
pip list       # Should show installed packages
```

**Test API manually:**
```bash
# Start server and test in another terminal
curl http://localhost:8081/health
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `DEBUG` | Enable debug mode | `True` |
| `ENVIRONMENT` | Environment name | `development` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8081` |
| `DEFAULT_MODEL` | Default AI model | `anthropic/claude-3.5-sonnet` |

## Next Steps

1. Add authentication and rate limiting
2. Implement conversation history
3. Add more AI model integrations
4. Create frontend interface
5. Add logging and monitoring
6. Deploy to production

## License

This project is open source and available under the MIT License.
