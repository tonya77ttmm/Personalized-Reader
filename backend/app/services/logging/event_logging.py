import uuid
import logging
from datetime import datetime,timezone
from sqlalchemy.orm import Session

from ...models.db_models import Events, EventType, ScrollingEvents, ConfusionEvents, EyeTrackingEvents, Helps, Feedbacks, TriggerType, FeedbackRating
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from ...database import SessionLocal

from ...schemas.events import EventsCreate

logger=logging.getLogger(__name__)

def create_confusion_event(db:Session,
                           session_id:str,
                           status:int):
    """Create a new confusion event in the database."""
    event_id= str(uuid.uuid4())
    event=Events(
        id=event_id,
        session_id=session_id,
        timestamp=datetime.now(timezone.utc),
        event_type=EventType.CONFUSION
    )
    confusion_event=ConfusionEvents(
        event_id=event_id,
        status=status)
    

    try:
        db.add(event)
        db.add(confusion_event)
        db.commit()
        return event_id
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Error creating confusion event: %s", e)
        raise

def save_confusion_to_db(session_id:str, status: int):
    with SessionLocal() as db:
        return create_confusion_event(db, session_id, status)