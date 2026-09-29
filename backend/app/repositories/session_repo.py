from sqlalchemy.orm import Session
from app.models.session import SessionModel
from app.schemas.session import SessionCreate
from datetime import datetime, timezone

class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: SessionCreate | None = None, mode: str | None = None, topic: str | None = None) -> SessionModel:
        actual_mode = mode or (data.mode if data else "daily")
        actual_topic = topic or (data.topic if data else None)
        db_obj = SessionModel(
            mode=actual_mode,
            topic=actual_topic
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def get(self, session_id: str) -> SessionModel | None:
        return self.db.query(SessionModel).filter(SessionModel.id == session_id).first()

    def finish(self, session_id: str) -> SessionModel | None:
        db_obj = self.get(session_id)
        if db_obj:
            db_obj.ended_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def list_recent(self, limit: int = 20) -> list[SessionModel]:
        return self.db.query(SessionModel).order_by(SessionModel.started_at.desc()).limit(limit).all()
