"""
SQLAlchemy database models for documents and pages.
"""

# from enum import Enum
import enum

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from ..database import Base

class EventType(str, enum.Enum):
    CONFUSION="confusion_event"
    EYE_TRACKING="eye_tracking_event"
    SCROLLING="scrolling_event"
    HELP="help_event"
    FEEDBACK="feedback_event"

class TriggerType(str, enum.Enum):
    MANUAL="manual"
    AUTOMATIC="automatic"

class FeedbackRating(str, enum.Enum):
    USEFUL="useful"
    NOT_USEFUL="not_useful"
    BAD_TIMING="bad_timing"


class Users(Base):
    __tablename__="users"
    id = Column(String, primary_key=True, index=True)

class Articles(Base):
    __tablename__="articles"
    id = Column(String, primary_key=True, index=True)
    content= Column(Text, nullable=False)

class ReadingSessions(Base):
    __tablename__="reading_sessions"
    id = Column(String, primary_key=True,index=True)
    user_id=Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id=Column(String, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    started_at=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    ended_at=Column(DateTime, nullable=True)

class Events(Base):
    __tablename__="events"
    id= Column(String, primary_key=True, index=True)
    session_id= Column(String, ForeignKey("reading_sessions.id", ondelete="CASCADE"), nullable=False)
    timestamp=Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    event_type=Column(Enum(EventType, name="event_type_enum", values_callable=lambda x:[e.value for e in x]), nullable=False) 

class ScrollingEvents(Base):
    __tablename__="scrolling_events"
    event_id = Column(String, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    scroll_Y = Column(Integer, nullable=False)

class ConfusionEvents(Base):
    __tablename__="confusion_events"
    event_id= Column(String, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    status=Column(Integer, nullable=False)  # 1 for confused, 0 for not confused

class EyeTrackingEvents(Base):
    __tablename__="eye_tracking_events"
    event_id= Column(String, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    gaze_x=Column(Integer, nullable=False)
    gaze_y=Column(Integer, nullable=False)

class Helps(Base):
    __tablename__="helps"
    event_id= Column(String, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    original_text=Column(Text, nullable=False)
    context=Column(Text, nullable=False)
    explanation=Column(Text, nullable=False)
    confusion_id= Column(String, ForeignKey("confusion_events.event_id", ondelete="SET NULL"), nullable=True)
    eyetracking_id= Column(String, ForeignKey("eye_tracking_events.event_id", ondelete="SET NULL"), nullable=True)
    trigger_type=Column(Enum(TriggerType, name="trigger_type_enum", values_callable=lambda x:[e.value for e in x]), nullable=False)

class Feedbacks(Base):
    __tablename__="feedbacks"
    event_id= Column(String, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    help_id= Column(String, ForeignKey("helps.event_id", ondelete="CASCADE"), nullable=False)
    feedback_rating=Column(Enum(FeedbackRating, name="feedback_rating_enum", values_callable=lambda x:[e.value for e in x]), nullable=False)
   





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
