import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text
from app.core.database import Base

class MistakeModel(Base):
    __tablename__ = "mistakes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, default="default", index=True)
    owner_user_id = Column(String, nullable=False, default="default", index=True)
    session_id = Column(String, nullable=True, index=True)
    turn_id = Column(String, nullable=True, index=True)
    category = Column(String, default="grammar")
    error_type = Column(String, default="grammar", index=True)
    subtype = Column(String, default="general", index=True)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    severity = Column(Integer, default=2)
    first_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    occurrence_count = Column(Integer, default=1)
    resolved = Column(Boolean, default=False)
    successful_reuse_count = Column(Integer, default=0)
    next_review_at = Column(DateTime, nullable=True, index=True)
    last_reviewed_at = Column(DateTime, nullable=True)
    mastery_state = Column(String, default="learning", index=True)
    example_sentence = Column(Text, nullable=True)
