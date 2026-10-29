import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, UniqueConstraint
from app.core.database import Base

class AdaptivePlanModel(Base):
    __tablename__ = "adaptive_plans"
    __table_args__ = (UniqueConstraint("owner_user_id", "plan_date", name="uq_adaptive_plan_owner_date"),)

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id = Column(String, nullable=False, index=True)
    plan_date = Column(String, nullable=False, index=True)
    payload_json = Column(Text, nullable=False)
    evidence_count = Column(String, default="0")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
