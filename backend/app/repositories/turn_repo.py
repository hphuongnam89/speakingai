from sqlalchemy.orm import Session
from app.models.turn import TurnModel

class TurnRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, session_id: str, role: str, transcript: str, audio_path: str | None = None, duration_ms: int = 0, owner_user_id: str = "default", client_turn_id: str | None = None) -> TurnModel:
        db_obj = TurnModel(
            session_id=session_id,
            owner_user_id=owner_user_id,
            client_turn_id=client_turn_id,
            role=role,
            transcript=transcript,
            audio_path=audio_path,
            duration_ms=duration_ms
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_client_turn_id(self, session_id: str, client_turn_id: str, owner_user_id: str | None = None) -> TurnModel | None:
        query = self.db.query(TurnModel).filter(
            TurnModel.session_id == session_id,
            TurnModel.client_turn_id == client_turn_id
        )
        if owner_user_id is not None:
            query = query.filter(TurnModel.owner_user_id == owner_user_id)
        return query.first()

    def get_by_session(self, session_id: str, owner_user_id: str | None = None) -> list[TurnModel]:
        query = self.db.query(TurnModel).filter(TurnModel.session_id == session_id)
        if owner_user_id is not None:
            query = query.filter(TurnModel.owner_user_id == owner_user_id)
        return query.order_by(TurnModel.created_at.asc()).all()

    def get(self, turn_id: str, owner_user_id: str | None = None) -> TurnModel | None:
        query = self.db.query(TurnModel).filter(TurnModel.id == turn_id)
        if owner_user_id is not None:
            query = query.filter(TurnModel.owner_user_id == owner_user_id)
        return query.first()
