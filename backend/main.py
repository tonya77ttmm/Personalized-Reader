from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.api.documents import router as documents_router
from app.api.explanations import router as explanations_router
from app.database import init_db

# Load environment variables
load_dotenv()
frontend_url = os.getenv("FRONTEND_URL")

app = FastAPI(
    title="AI Reader Agent API",
    description="Backend API for AI Reader Agent - personalized reading assistance",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(documents_router)
app.include_router(explanations_router)

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