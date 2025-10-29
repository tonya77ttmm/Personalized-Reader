# AI Reader Agent - Backend

FastAPI backend for the AI Reader Agent application.

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run Development Server

```bash
# Option 1: Using the development script
python run_dev.py

# Option 2: Using uvicorn directly
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- **Health Check**: `GET /health`
- **Root**: `GET /`
- **API Documentation**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Project Structure

```
backend/
├── app/                    # Application modules
│   ├── api/               # API routes
│   ├── core/              # Core functionality
│   ├── models/            # Data models
│   └── services/          # Business logic
├── venv/                  # Virtual environment
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── run_dev.py            # Development server script
```

## Dependencies

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type annotations
- **python-dotenv**: Environment variable management
- **httpx**: HTTP client for testing and external API calls
- **python-multipart**: File upload support

## Development

The server runs with auto-reload enabled, so changes to the code will automatically restart the server.

Access the interactive API documentation at `http://localhost:8000/docs` to test endpoints.
