from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExplanationRequest(BaseModel):
    """Request model for text explanation."""
    text: str
    context: Optional[str] = None


class ExplanationResponse(BaseModel):
    """Response model for text explanation."""
    text: str
    explanation: str
    context_used: bool
    response_time_ms: int