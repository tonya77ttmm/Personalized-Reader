"""
Document processing and storage service.
"""

import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import math

from sqlalchemy.orm import Session

from ..models.document import DocumentMetadata, DocumentResponse
from ..models.db_models import Document, DocumentPage
from ..database import SessionLocal


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
    
    def calculate_context_windows(
        self,
        pages: List[Dict],
        window_size: int = 100
    ) -> List[Dict]:
        """
        Calculate context windows for each page.
        
        Extracts the last N words from the previous page as context_before
        and the first N words from the next page as context_after.
        
        Args:
            pages: List of page dictionaries with content
            window_size: Number of words to include in context (default: 100)
            
        Returns:
            List of page dictionaries with context_before and context_after added
        """
        for i, page in enumerate(pages):
            # Handle context_before (last N words from previous page)
            if i == 0:
                # First page has no previous context
                page['context_before'] = ""
            else:
                previous_page_content = pages[i - 1]['content']
                previous_words = previous_page_content.split()
                # Get last window_size words from previous page
                context_words = previous_words[-window_size:] if len(previous_words) > window_size else previous_words
                page['context_before'] = ' '.join(context_words)
            
            # Handle context_after (first N words from next page)
            if i == len(pages) - 1:
                # Last page has no next context
                page['context_after'] = ""
            else:
                next_page_content = pages[i + 1]['content']
                next_words = next_page_content.split()
                # Get first window_size words from next page
                context_words = next_words[:window_size] if len(next_words) > window_size else next_words
                page['context_after'] = ' '.join(context_words)
        
        return pages
    
    def split_document_into_pages(
        self, 
        content: str, 
        words_per_page: int = 500
    ) -> List[Dict]:
        """
        Split document content into pages based on word count.
        
        Args:
            content: Full document text
            words_per_page: Target words per page (default: 500)
            
        Returns:
            List of page dictionaries with content and metadata
        """
        # Split content into words
        words = content.split()
        total_words = len(words)
        pages = []
        
        # Calculate number of pages
        page_count = math.ceil(total_words / words_per_page)  # Ceiling division
        
        # Split into pages
        for page_num in range(page_count):
            start_word_index = page_num * words_per_page
            end_word_index = min(start_word_index + words_per_page, total_words)
            
            # Extract words for this page
            page_words = words[start_word_index:end_word_index]
            page_content = ' '.join(page_words)
            
            # Create page data
            page_data = {
                'page_number': page_num + 1,  # Page numbers start from 1
                'content': page_content,
                'start_word_index': start_word_index,
                'end_word_index': end_word_index,
                'word_count': len(page_words)
            }
            
            pages.append(page_data)
        
        return pages
    
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
    
    def store_document(self, content: bytes, filename: str, words_per_page: int = 500) -> DocumentResponse:
        """
        Store document content and metadata, including page splitting.
        
        Args:
            content: Raw file content bytes
            filename: Original filename
            words_per_page: Number of words per page (default: 500)
            
        Returns:
            DocumentResponse with document details
        """
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Process text content
        processed = self.process_text_content(content, filename)
        text_content = processed['content']
        
        # Split document into pages
        pages = self.split_document_into_pages(text_content, words_per_page)
        
        # Calculate context windows for pages
        pages = self.calculate_context_windows(pages)
        
        # Create metadata
        metadata = DocumentMetadata(
            file_type="text/plain",
            file_size=len(content),
            word_count=processed['word_count'],
            estimated_reading_time=processed['estimated_reading_time'],
            language=processed['language']
        )
        
        # Store content to file (for backward compatibility)
        content_file = self.storage_path / "content" / f"{document_id}.txt"
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # Store metadata to file (for backward compatibility)
        metadata_file = self.storage_path / "metadata" / f"{document_id}.json"
        document_data = {
            'id': document_id,
            'title': filename or f"document_{document_id[:8]}",
            'metadata': metadata.model_dump(),
            'uploaded_at': datetime.now().isoformat(),
            'preview': processed['preview'],
            'char_count': processed['char_count'],
            'line_count': processed['line_count'],
            'total_pages': len(pages),
            'words_per_page': words_per_page
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(document_data, f, indent=2)
        
        # Store document and pages in database
        db = SessionLocal()
        try:
            # Create document record
            db_document = Document(
                id=document_id,
                title=filename or f"document_{document_id[:8]}",
                content=text_content,
                file_type="text/plain",
                file_size=len(content),
                word_count=processed['word_count'],
                estimated_reading_time=processed['estimated_reading_time'],
                language=processed['language'],
                total_pages=len(pages),
                words_per_page=words_per_page,
                uploaded_at=datetime.now()
            )
            db.add(db_document)
            
            # Create page records
            for page in pages:
                page_id = str(uuid.uuid4())
                db_page = DocumentPage(
                    id=page_id,
                    document_id=document_id,
                    page_number=page['page_number'],
                    content=page['content'],
                    start_word_index=page['start_word_index'],
                    end_word_index=page['end_word_index'],
                    word_count=page['word_count'],
                    context_before=page['context_before'],
                    context_after=page['context_after'],
                    created_at=datetime.now()
                )
                db.add(db_page)
            
            # Commit all changes
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
        
        # Return response
        return DocumentResponse(
            id=document_id,
            title=filename or f"document_{document_id[:8]}",
            metadata=metadata,
            uploaded_at=datetime.now(),
            message=f"Document processed and stored successfully with {len(pages)} pages"
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
    
    def get_document_metadata(self, document_id: str) -> Optional[Dict]:
        """
        Retrieve document metadata by ID from database.
        
        Args:
            document_id: Document ID to retrieve
            
        Returns:
            Document metadata or None if not found
        """
        db = SessionLocal()
        try:
            # Query document from database
            db_document = db.query(Document).filter(Document.id == document_id).first()
            
            if not db_document:
                return None
            
            # Return metadata
            return {
                'id': db_document.id,
                'title': db_document.title,
                'total_pages': db_document.total_pages,
                'total_words': db_document.word_count,
                'words_per_page': db_document.words_per_page,
                'uploaded_at': db_document.uploaded_at.isoformat()
            }
        finally:
            db.close()
    
    def get_document_page(self, document_id: str, page_number: int) -> Optional[Dict]:
        """
        Retrieve a specific page from a document by ID and page number.
        
        Args:
            document_id: Document ID to retrieve page from
            page_number: Page number to retrieve (1-indexed)
            
        Returns:
            Page data with content and context windows, or None if not found
        """
        db = SessionLocal()
        try:
            # First verify document exists
            db_document = db.query(Document).filter(Document.id == document_id).first()
            
            if not db_document:
                return None
            
            # Validate page number
            if page_number < 1 or page_number > db_document.total_pages:
                return None
            
            # Query specific page
            db_page = db.query(DocumentPage).filter(
                DocumentPage.document_id == document_id,
                DocumentPage.page_number == page_number
            ).first()
            
            if not db_page:
                return None
            
            # Return page data
            return {
                'page_number': db_page.page_number,
                'content': db_page.content,
                'start_word_index': db_page.start_word_index,
                'end_word_index': db_page.end_word_index,
                'word_count': db_page.word_count,
                'context_before': db_page.context_before,
                'context_after': db_page.context_after
            }
        finally:
            db.close()
    
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