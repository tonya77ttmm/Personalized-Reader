from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = FastAPI(
    title="AI Reader Agent API",
    description="Backend API for AI Reader Agent - personalized reading assistance",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],  # Frontend URL as list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Reader Agent API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-reader-api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)