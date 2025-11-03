# AI Reader Agent

A personalized AI-powered reading assistant that helps users comprehend and learn from text documents through contextual explanations and adaptive learning features.

## Features

- **Text Upload**: Import and read TXT files with a clean, responsive interface
- **AI Explanations**: Get contextual explanations for difficult words and phrases
- **Smart Highlighting**: Automatic highlighting based on text complexity
- **Reading Progress**: Track your learning journey and vocabulary growth

## Tech Stack

### Frontend

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation

### Backend

- **Python 3.9+** with FastAPI
- **Uvicorn** ASGI server
- **Pydantic** for data validation
- **OpenAI API** for AI explanations

## Quick Start

### Prerequisites

- npm
- Python 3.9+
- pip

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd ai-reader-agent
   ```

2. **Install all dependencies**

   ```bash
   npm run install:all
   ```

3. **Set up environment variables**

   ```bash
   cd backend
   ...
   ```

4. **Start development servers**
   ```bash
   npm run dev
   ```

This will start:

- Frontend at http://localhost:3000
- Backend API at http://localhost:8000

### Individual Commands

- **Frontend only**: `npm run dev:frontend`
- **Backend only**: "source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
- **Build for production**: `npm run build`
- **Lint code**: `npm run lint`

## Project Structure

```
ai-reader-agent/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   └── ...
│   └── package.json
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── core/           # Configuration
│   ├── main.py             # Application entry point
│   └── requirements.txt
└── package.json            # Root package.json for scripts
```

## Development

### Adding New Features

1. **Frontend Components**: Add to `frontend/src/components/`
2. **API Endpoints**: Add to `backend/app/api/`
3. **Data Models**: Add to `backend/app/models/`
4. **Business Logic**: Add to `backend/app/services/`

### API Documentation

When the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details
