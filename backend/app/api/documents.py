"""
Document upload and management API endpoints.
"""

import asyncio
import uuid
import os
from datetime import datetime
from typing import List
from pathlib import Path
from fastapi import APIRouter, File,  UploadFile, HTTPException, WebSocket, status
from fastapi.responses import JSONResponse

from ..models.document import DocumentResponse, DocumentMetadataResponse, PageDataResponse, ErrorResponse
from ..services.document_service import DocumentService
from ..services.confusion_service import ConfusionService

# Optional import for python-magic (requires system libmagic)
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False


router = APIRouter(prefix="/api/documents", tags=["documents"])

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".txt"}
ALLOWED_MIME_TYPES = {"text/plain"}

# Initialize document service
document_service = DocumentService()
confusion_service = ConfusionService()  # Placeholder for actual model

def validate_file(file: UploadFile, content: bytes) -> None:
    """
    Validate uploaded file for type, size, and content.
    
    Args:
        file: The uploaded file to validate
        content: File content bytes for validation
        
    Raises:
        HTTPException: If file validation fails
    """
    # Check file extension
    if file.filename:
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed."
            )
    
    # Check MIME type from browser
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Expected text/plain, got {file.content_type}"
        )
    
    # Check file size
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
    
    # Validate content with python-magic (if available)
    if MAGIC_AVAILABLE:
        try:
            file_type = magic.from_buffer(content, mime=True)
            if file_type not in ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File content validation failed. Expected text file, detected: {file_type}"
                )
        except Exception:
            # If magic fails, we'll rely on other validation methods
            pass
    
    # Validate content is valid UTF-8 text
    try:
        content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must contain valid UTF-8 text"
        )


@router.websocket("/ws")
async def reading_ws(websocket:WebSocket):
    await websocket.accept()
    print("Client connected!", flush=True)
    try:
        while True:
            frame=await websocket.receive_bytes()
            # Save the frame for debugging
            # Path("debug").mkdir(exist_ok=True)

            # with open("debug/latest_frame.png","wb") as f:

            #     f.write(frame)

            # print("saved frame", flush=True)
            # prediction=confusion_service.predict(frame)
            prediction = await asyncio.to_thread(confusion_service.predict,frame)
            print("Prediction:", prediction , flush=True)
            await websocket.send_json({"confusion_prob":prediction})
    except Exception as e:
        print(f"WebSocket error: {e}")


@router.post("/", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a text document for processing.
    
    Args:
        file: The text file to upload (TXT format only)
        
    Returns:
        DocumentResponse: Document details with ID and metadata
        
    Raises:
        HTTPException: If file validation fails or upload processing fails
    """
    try:
        # Read file content
        content = await file.read()
        
        # Validate the uploaded file (includes all validation: type, size, content)
        validate_file(file, content)
        
        # Process and store the document
        document_response = document_service.store_document(content, file.filename)
        
        return document_response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


# @router.get("/")
# async def list_documents():
#     """
#     List all uploaded documents.
    
#     Returns:
#         List of document metadata
#     """
#     try:
#         documents = document_service.list_documents()
#         return {
#             "documents": documents,
#             "count": len(documents),
#             "message": "Documents retrieved successfully"
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to list documents: {str(e)}"
#         )


@router.get("/{document_id}/metadata", response_model=DocumentMetadataResponse)
async def get_document_metadata(document_id: str):
    """
    Get document metadata by ID.
    
    Args:
        document_id: The document ID to retrieve metadata for
        
    Returns:
        DocumentMetadataResponse: Document metadata including total_pages, total_words, words_per_page
        
    Raises:
        HTTPException: 404 if document not found, 500 for server errors
    """
    try:
        metadata = document_service.get_document_metadata(document_id)
        
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document metadata: {str(e)}"
        )


@router.get("/{document_id}/pages/{page_number}", response_model=PageDataResponse)
async def get_document_page(document_id: str, page_number: int):
    """
    Get a specific page from a document by ID and page number.
    
    Args:
        document_id: The document ID to retrieve page from
        page_number: The page number to retrieve (1-indexed)
        
    Returns:
        PageDataResponse: Page content with context windows
        
    Raises:
        HTTPException: 404 if document or page not found, 400 for invalid page numbers, 500 for server errors
    """
    try:
        # Validate page number
        if page_number < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid page number: {page_number}. Page numbers must be >= 1"
            )
        
        # Fetch page from service
        page_data = document_service.get_document_page(document_id, page_number)
        
        if not page_data:
            # Check if document exists to provide better error message
            metadata = document_service.get_document_metadata(document_id)
            if not metadata:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Document with ID {document_id} not found"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Page {page_number} not found. Document has {metadata['total_pages']} pages"
                )
        
        return page_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve page: {str(e)}"
        )


@router.get("/{document_id}")
async def get_document(document_id: str):
    """
    Get a specific document by ID.
    
    Args:
        document_id: The document ID to retrieve
        
    Returns:
        Document details including content
    """
    try:
        document = document_service.get_document(document_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}"
        )


# @router.delete("/{document_id}")
# async def delete_document(document_id: str):
#     """
#     Delete a document by ID.
    
#     Args:
#         document_id: The document ID to delete
        
#     Returns:
#         Deletion confirmation
#     """
#     try:
#         deleted = document_service.delete_document(document_id)
        
#         if not deleted:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Document with ID {document_id} not found"
#             )
        
#         return {
#             "message": f"Document {document_id} deleted successfully",
#             "deleted": True
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to delete document: {str(e)}"
#         )