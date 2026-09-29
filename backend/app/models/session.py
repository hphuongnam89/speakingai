import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, default="default")
    mode = Column(String, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    topic = Column(String, nullable=True)
    total_speaking_ms = Column(Integer, default=0)
    estimated_band = Column(Float, nullable=True)
    evaluation_json = Column(String, nullable=True)
    provider = Column(String, nullable=True)

    turns = relationship("TurnModel", back_populates="session")

