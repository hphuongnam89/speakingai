import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, Integer, String, Boolean, Text
from app.core.database import Base


class ProfileModel(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    owner_user_id = Column(String, nullable=False, default="default", index=True)
    avatar_color = Column(String, default="#4f46e5")
    current_band = Column(Float, nullable=True)
    target_band = Column(Float, default=7.0)
    daily_target_minutes = Column(Integer, default=20)
    target_duration_months = Column(Integer, default=3)
    placement_status = Column(String, default="not_started")  # not_started, completed
    roadmap_data = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_active_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
