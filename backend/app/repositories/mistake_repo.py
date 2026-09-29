from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.mistake import MistakeModel

class MistakeRepository:
    def __init__(self, db: Session):
        self.db = db

    def record_mistake(
        self,
        user_id: str,
        session_id: str | None,
        turn_id: str | None,
        original: str,
        corrected: str,
        explanation: str | None = None,
        category: str = "grammar",
        severity: int = 2
    ) -> MistakeModel:
        cleaned_orig = original.strip().lower()
        
        # Check if identical mistake was recorded previously for this user
        existing = (
            self.db.query(MistakeModel)
            .filter(
                MistakeModel.user_id == user_id,
                func.lower(MistakeModel.original_text) == cleaned_orig
            )
            .first()
        )

        now = datetime.now(timezone.utc)
        if existing:
            existing.occurrence_count += 1
            existing.last_seen_at = now
            existing.session_id = session_id or existing.session_id
            existing.turn_id = turn_id or existing.turn_id
            existing.corrected_text = corrected
            if explanation:
                existing.explanation = explanation
            existing.resolved = False
            self.db.commit()
            self.db.refresh(existing)
            return existing

        new_mistake = MistakeModel(
            user_id=user_id,
            session_id=session_id,
            turn_id=turn_id,
            category=category,
            original_text=original.strip(),
            corrected_text=corrected.strip(),
            explanation=explanation,
            severity=severity,
            first_seen_at=now,
            last_seen_at=now,
            occurrence_count=1,
            resolved=False
        )
        self.db.add(new_mistake)
        self.db.commit()
        self.db.refresh(new_mistake)
        return new_mistake

    def list_mistakes(
        self,
        user_id: str = "default",
        limit: int = 50,
        resolved: bool | None = None
    ) -> list[MistakeModel]:
        query = self.db.query(MistakeModel).filter(MistakeModel.user_id == user_id)
        if resolved is not None:
            query = query.filter(MistakeModel.resolved == resolved)
        return query.order_by(MistakeModel.last_seen_at.desc()).limit(limit).all()

    def get_frequent_mistakes(
        self,
        user_id: str = "default",
        limit: int = 10
    ) -> list[MistakeModel]:
        return (
            self.db.query(MistakeModel)
            .filter(MistakeModel.user_id == user_id)
            .order_by(MistakeModel.occurrence_count.desc(), MistakeModel.last_seen_at.desc())
            .limit(limit)
            .all()
        )

    def resolve_mistake(self, mistake_id: str) -> MistakeModel | None:
        mistake = self.db.query(MistakeModel).filter(MistakeModel.id == mistake_id).first()
        if mistake:
            mistake.resolved = True
            self.db.commit()
            self.db.refresh(mistake)
        return mistake
