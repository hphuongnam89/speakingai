from sqlalchemy.orm import Session
from app.models.session import SessionModel
from app.schemas.session import SessionCreate
from datetime import datetime, timezone

class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: SessionCreate | None = None, mode: str | None = None, topic: str | None = None, user_id: str = "default") -> SessionModel:
        actual_mode = mode or (data.mode if data else "daily")
        actual_topic = topic or (data.topic if data else None)
        db_obj = SessionModel(
            mode=actual_mode,
            topic=actual_topic,
            user_id=user_id
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def get(self, session_id: str, user_id: str | None = None) -> SessionModel | None:
        query = self.db.query(SessionModel).filter(SessionModel.id == session_id)
        if user_id is not None:
            query = query.filter(SessionModel.user_id == user_id)
        return query.first()

    def finish(self, session_id: str, user_id: str | None = None) -> SessionModel | None:
        db_obj = self.get(session_id, user_id)
        if db_obj:
            db_obj.ended_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def list_recent(self, limit: int = 20, user_id: str | None = None) -> list[SessionModel]:
        query = self.db.query(SessionModel)
        if user_id is not None:
            query = query.filter(SessionModel.user_id == user_id)
        return query.order_by(SessionModel.started_at.desc()).limit(limit).all()
