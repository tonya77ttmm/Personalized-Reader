"""
AI explanation API endpoints.
"""

import os
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from dotenv import load_dotenv


load_dotenv()

router = APIRouter(prefix="/api/explanations", tags=["explanations"])

output_parser = StrOutputParser()

model = ChatOpenAI(
            temperature=0,
            model="gpt-4.1-mini",
        )
# Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful reading assistant. Explain words, idioms, or technical terms based on the context. Keep explanations clear, concise, and under 50 words. Focus on meaning and cultural context."),
    ("user", "Explain this text: '{text}'\n\nContext: {context}")
])
# Create the chain
explanation_chain = prompt | model|output_parser

class ExplanationRequest(BaseModel):
    """Request model for text explanation."""
    text: str
    context: Optional[str] = None
    document_title: Optional[str] = None


class ExplanationResponse(BaseModel):
    """Response model for text explanation."""
    text: str
    explanation: str
    context_used: bool
    response_time_ms: int


@router.post("/", response_model=ExplanationResponse)
async def get_explanation(request: ExplanationRequest):
    """
    Get AI explanation for selected text.
    
    Args:
        request: Text and optional context for explanation
        
    Returns:
        ExplanationResponse: AI-generated explanation
        
    Raises:
        HTTPException: If explanation generation fails
    """
    import time
    start_time = time.time()
    
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        if len(request.text) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text too long. Maximum 1000 characters allowed."
            )
        
        # Generate explanation
        if explanation_chain:
            # Use LangChain - super simple!
            context = request.context or "No additional context provided."
            
            explanation = response = explanation_chain.invoke({
                "text": request.text,
                "context": context
            })
        
        response_time = int((time.time() - start_time) * 1000)
        
        return ExplanationResponse(
            text=request.text,
            explanation=explanation,
            context_used=bool(request.context),
            response_time_ms=response_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}"
        )

@router.get("/health")
async def explanation_health():
    """Health check for explanation service."""
    return {
        "status": "healthy",
        "langchain_configured": explanation_chain is not None,
        "service": "explanation-api"
    }