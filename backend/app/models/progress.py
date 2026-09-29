import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Date
from app.core.database import Base

class DailyStatsModel(Base):
    __tablename__ = "daily_stats"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, default="default", index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    speaking_minutes = Column(Float, default=0.0)
    session_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    avg_wpm = Column(Float, default=0.0)
    mistake_count = Column(Integer, default=0)
    estimated_band = Column(Float, nullable=True)
