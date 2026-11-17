
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

class EventsCreate(BaseModel): 
    session_id: str