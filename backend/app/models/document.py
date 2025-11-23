"""
Document models for the AI Reader Agent.
FastAPI uses BaseModel for request/response:
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentMetadata(BaseModel):
    """Metadata for uploaded documents."""
    file_type: str
    file_size: int  # in bytes
    word_count: int
    estimated_reading_time: int  # in minutes
    language: str = "en"


class DocumentResponse(BaseModel):
    """Response model for document operations."""
    id: str
    title: str
    metadata: DocumentMetadata
    uploaded_at: datetime
    message: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str
    status_code: int