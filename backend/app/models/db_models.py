"""
SQLAlchemy database models for documents and pages.
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class Document(Base):
    """
    Document model for storing document metadata.
    """
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Full content for backward compatibility
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    estimated_reading_time = Column(Integer, nullable=False)
    language = Column(String, default="en")
    
    # New fields for pagination
    total_pages = Column(Integer, nullable=True)
    words_per_page = Column(Integer, default=500)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to pages
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")


class DocumentPage(Base):
    """
    DocumentPage model for storing individual pages of a document.
    """
    __tablename__ = "document_pages"
    
    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    start_word_index = Column(Integer, nullable=False)
    end_word_index = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    context_before = Column(Text, default="")
    context_after = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to document
    document = relationship("Document", back_populates="pages")
    
    # Create composite index for efficient querying
    __table_args__ = (
        Index('idx_document_page', 'document_id', 'page_number'),
    )
