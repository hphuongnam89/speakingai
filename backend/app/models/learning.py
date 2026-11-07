import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Text, DateTime, UniqueConstraint

from app.core.database import Base


class LearningLessonModel(Base):
    __tablename__ = "learning_lessons"
    id = Column(String, primary_key=True)
    version = Column(String, primary_key=True)
    checksum = Column(String, nullable=False)
    payload_json = Column(Text, nullable=False)


class LearningAttemptModel(Base):
    __tablename__ = "learning_attempts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id = Column(String, nullable=False, index=True)
    profile_id = Column(String, nullable=False, index=True)
    lesson_id = Column(String, nullable=False)
    lesson_version = Column(String, nullable=False)
    create_key = Column(String, nullable=False)
    revision = Column(Integer, nullable=False, default=0)
    step_id = Column(String, nullable=False)
    draft = Column(Text, nullable=False, default="")
    drafts_json = Column(Text, nullable=False, default="{}")
    assistance_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (UniqueConstraint("owner_user_id", "profile_id", "create_key"),)


class LearningEventModel(Base):
    __tablename__ = "learning_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id = Column(String, nullable=False, index=True)
    profile_id = Column(String, nullable=False, index=True)
    attempt_id = Column(String, nullable=False, index=True)
    request_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    request_hash = Column(String, nullable=False)
    response_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (UniqueConstraint("attempt_id", "action", "request_id"),)


class LearningObservationModel(Base):
    __tablename__ = "learning_observations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id = Column(String, nullable=False, index=True)
    profile_id = Column(String, nullable=False, index=True)
    attempt_id = Column(String, nullable=False, index=True)
    lesson_id = Column(String, nullable=False)
    lesson_version = Column(String, nullable=False)
    item_id = Column(String, nullable=False)
    competency_id = Column(String, nullable=False)
    evidence_kind = Column(String, nullable=False)
    result = Column(String, nullable=False)
    response_text = Column(Text, nullable=False)
    assistance_json = Column(Text, nullable=False)
    policy_version = Column(String, nullable=False, default="learning-foundation-0.1")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class LearningReviewModel(Base):
    __tablename__ = "learning_reviews"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id = Column(String, nullable=False, index=True)
    profile_id = Column(String, nullable=False, index=True)
    lesson_id = Column(String, nullable=False)
    lesson_version = Column(String, nullable=False)
    item_id = Column(String, nullable=False)
    competency_id = Column(String, nullable=False)
    state = Column(String, nullable=False, default="learning")
    interval_days = Column(Integer, nullable=False, default=1)
    next_review_at = Column(DateTime, nullable=False, index=True)
    last_result = Column(String, nullable=False)
    last_evidence_kind = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (UniqueConstraint("owner_user_id", "profile_id", "lesson_id", "lesson_version", "item_id"),)
