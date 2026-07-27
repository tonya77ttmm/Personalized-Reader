"""
Schemas
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


class DocumentMetadataResponse(BaseModel):
    """Response model for document metadata endpoint."""
    id: str
    title: str
    total_pages: int
    total_words: int
    words_per_page: int
    uploaded_at: datetime


class PageDataResponse(BaseModel):
    """Response model for document page endpoint."""
    page_number: int
    content: str
    start_word_index: int
    end_word_index: int
    word_count: int
    context_before: str
    context_after: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str
    status_code: int