import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.core.database import Base


class AudioRecordingModel(Base):
    __tablename__ = "audio_recordings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id = Column(String, nullable=False, index=True, default="default")
    session_id = Column(String, ForeignKey("sessions.id"), nullable=True, index=True)
    turn_id = Column(String, ForeignKey("turns.id"), nullable=True, index=True)
    file_path = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    retention_at = Column(DateTime, nullable=True, index=True)
