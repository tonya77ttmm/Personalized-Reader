"""
Document processing and storage service.
"""

import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re

from ..models.document import DocumentMetadata, DocumentResponse


class DocumentService:
    """Service for processing and storing documents."""
    
    def __init__(self, storage_path: str = "storage/documents"):
        """
        Create ducument storage path
        Initialize the document service. 
        
        Args:
            storage_path: Path to store documents (relative to backend root)
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.storage_path / "content").mkdir(exist_ok=True)
        (self.storage_path / "metadata").mkdir(exist_ok=True)
    
    def process_text_content(self, content: bytes, filename: str) -> Dict:
        """
        Process uploaded text content and extract metadata.
        
        Args:
            content: Raw file content bytes
            filename: Original filename
            
        Returns:
            Dict containing processed text and metadata
        """
        # Decode content to text
        text_content = content.decode('utf-8')
        
        # Calculate basic metadata
        word_count = len(text_content.split())
        char_count = len(text_content)
        line_count = len(text_content.splitlines())
        
        # Estimate reading time (average 200 words per minute)
        estimated_reading_time = max(1, word_count // 200)
        
        # Extract first few words for preview
        words = text_content.split()
        preview = ' '.join(words[:20]) + ('...' if len(words) > 20 else '')
        
        return {
            'content': text_content,
            'word_count': word_count,
            'char_count': char_count,
            'line_count': line_count,
            'estimated_reading_time': estimated_reading_time,
            'preview': preview,
            'language': 'en'  # Default to English for now
        }
    
    def store_document(self, content: bytes, filename: str) -> DocumentResponse:
        """
        Store document content and metadata.
        
        Args:
            content: Raw file content bytes
            filename: Original filename
            
        Returns:
            DocumentResponse with document details
        """
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Process text content
        processed = self.process_text_content(content, filename)
        
        # Create metadata
        metadata = DocumentMetadata(
            file_type="text/plain",
            file_size=len(content),
            word_count=processed['word_count'],
            estimated_reading_time=processed['estimated_reading_time'],
            language=processed['language']
        )
        
        # Store content to file
        content_file = self.storage_path / "content" / f"{document_id}.txt"
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(processed['content'])
        
        # Store metadata to file
        metadata_file = self.storage_path / "metadata" / f"{document_id}.json"
        document_data = {
            'id': document_id,
            'title': filename or f"document_{document_id[:8]}",
            'metadata': metadata.model_dump(),
            'uploaded_at': datetime.now().isoformat(),
            'preview': processed['preview'],
            'char_count': processed['char_count'],
            'line_count': processed['line_count']
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(document_data, f, indent=2)
        
        # Return response
        return DocumentResponse(
            id=document_id,
            title=filename or f"document_{document_id[:8]}",
            metadata=metadata,
            uploaded_at=datetime.now(),
            message="Document processed and stored successfully"
        )
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """
        Retrieve document by ID.
        
        Args:
            document_id: Document ID to retrieve
            
        Returns:
            Document data or None if not found
        """
        metadata_file = self.storage_path / "metadata" / f"{document_id}.json"
        content_file = self.storage_path / "content" / f"{document_id}.txt"
        
        if not metadata_file.exists() or not content_file.exists():
            return None
        
        # Load metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Load content
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            **metadata,
            'content': content
        }
    
    # def list_documents(self) -> List[Dict]:
    #     """
    #     List all stored documents.
        
    #     Returns:
    #         List of document metadata
    #     """
    #     documents = []
    #     metadata_dir = self.storage_path / "metadata"
        
    #     for metadata_file in metadata_dir.glob("*.json"):
    #         try:
    #             with open(metadata_file, 'r', encoding='utf-8') as f:
    #                 doc_data = json.load(f)
    #                 # Don't include full content in list view
    #                 doc_data.pop('content', None)
    #                 documents.append(doc_data)
    #         except Exception:
    #             # Skip corrupted files
    #             continue
        
    #     # Sort by upload date (newest first)
    #     documents.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
    #     return documents
    
    # def delete_document(self, document_id: str) -> bool:
    #     """
    #     Delete a document by ID.
        
    #     Args:
    #         document_id: Document ID to delete
            
    #     Returns:
    #         True if deleted, False if not found
    #     """
    #     metadata_file = self.storage_path / "metadata" / f"{document_id}.json"
    #     content_file = self.storage_path / "content" / f"{document_id}.txt"
        
    #     deleted = False
        
    #     if metadata_file.exists():
    #         metadata_file.unlink()
    #         deleted = True
        
    #     if content_file.exists():
    #         content_file.unlink()
    #         deleted = True
        
    #     return deleted