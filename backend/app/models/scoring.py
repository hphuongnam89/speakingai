import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Float
from app.core.database import Base

class EvaluationFeedbackModel(Base):
    __tablename__ = "evaluation_feedback"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, index=True)
    owner_user_id = Column(String, nullable=False, index=True)
    flag = Column(String, nullable=False)
    comment = Column(Text, nullable=True)
    scoring_version = Column(String, nullable=False, default="phase8-v1")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CalibrationSampleModel(Base):
    __tablename__ = "calibration_samples"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sample_key = Column(String, nullable=False, unique=True, index=True)
    level = Column(String, nullable=False)
    transcript = Column(Text, nullable=False)
    human_fc = Column(Float, nullable=True)
    human_lr = Column(Float, nullable=True)
    human_gra = Column(Float, nullable=True)
    human_pronunciation = Column(Float, nullable=True)
    ai_payload_json = Column(Text, nullable=True)
    consented = Column(String, nullable=False, default="false")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
