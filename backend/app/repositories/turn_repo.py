from sqlalchemy.orm import Session
from app.models.turn import TurnModel

class TurnRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session_id: str, role: str, transcript: str, audio_path: str | None = None, duration_ms: int = 0) -> TurnModel:
        db_obj = TurnModel(
            session_id=session_id,
            role=role,
            transcript=transcript,
            audio_path=audio_path,
            duration_ms=duration_ms
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_session(self, session_id: str) -> list[TurnModel]:
        return self.db.query(TurnModel).filter(TurnModel.session_id == session_id).order_by(TurnModel.created_at.asc()).all()

    def get(self, turn_id: str) -> TurnModel | None:
        return self.db.query(TurnModel).filter(TurnModel.id == turn_id).first()
