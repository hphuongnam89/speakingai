import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from app.core.database import Base

class PilotRunModel(Base):
    __tablename__ = "pilot_runs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id = Column(String, nullable=False, index=True)
    participant_code = Column(String, nullable=False, index=True)
    consent_audio = Column(Boolean, nullable=False, default=False)
    consent_feedback = Column(Boolean, nullable=False, default=False)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

class PilotEventModel(Base):
    __tablename__ = "pilot_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pilot_run_id = Column(String, nullable=False, index=True)
    owner_user_id = Column(String, nullable=False, index=True)
    task_key = Column(String, nullable=False)
    outcome = Column(String, nullable=False)
    help_used = Column(Boolean, nullable=False, default=False)
    understood_quote = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class PilotFeedbackModel(Base):
    __tablename__ = "pilot_feedback"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pilot_run_id = Column(String, nullable=False, unique=True, index=True)
    owner_user_id = Column(String, nullable=False, index=True)
    next_action_clear = Column(Integer, nullable=False)
    correction_useful = Column(Integer, nullable=False)
    score_too_certain = Column(Integer, nullable=False)
    would_return = Column(Integer, nullable=False)
    free_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
