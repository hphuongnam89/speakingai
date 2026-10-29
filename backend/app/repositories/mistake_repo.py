from datetime import datetime, timezone, timedelta
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
        severity: int = 2,
        owner_user_id: str = "default",
        error_type: str | None = None,
        subtype: str = "general",
        example_sentence: str | None = None
    ) -> MistakeModel:
        cleaned_orig = original.strip().lower()
        
        # Check if identical mistake was recorded previously for this user
        existing = (
            self.db.query(MistakeModel)
            .filter(
                MistakeModel.user_id == user_id,
                MistakeModel.owner_user_id == owner_user_id,
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
            existing.error_type = error_type or existing.error_type or category
            existing.subtype = subtype
            existing.example_sentence = example_sentence or existing.example_sentence
            if explanation:
                existing.explanation = explanation
            existing.resolved = False
            self.db.commit()
            self.db.refresh(existing)
            return existing

        new_mistake = MistakeModel(
            user_id=user_id,
            owner_user_id=owner_user_id,
            session_id=session_id,
            turn_id=turn_id,
            category=category,
            error_type=error_type or category,
            subtype=subtype,
            original_text=original.strip(),
            corrected_text=corrected.strip(),
            explanation=explanation,
            severity=severity,
            first_seen_at=now,
            last_seen_at=now,
            occurrence_count=1,
            resolved=False,
            mastery_state="learning",
            example_sentence=example_sentence
        )
        self.db.add(new_mistake)
        self.db.commit()
        self.db.refresh(new_mistake)
        return new_mistake

    def list_mistakes(
        self,
        user_id: str = "default",
        limit: int = 50,
        resolved: bool | None = None,
        owner_user_id: str | None = None
    ) -> list[MistakeModel]:
        query = self.db.query(MistakeModel).filter(MistakeModel.user_id == user_id)
        if owner_user_id is not None:
            query = query.filter(MistakeModel.owner_user_id == owner_user_id)
        if resolved is not None:
            query = query.filter(MistakeModel.resolved == resolved)
        return query.order_by(MistakeModel.last_seen_at.desc()).limit(limit).all()

    def get_frequent_mistakes(
        self,
        user_id: str = "default",
        limit: int = 10,
        owner_user_id: str | None = None
    ) -> list[MistakeModel]:
        query = self.db.query(MistakeModel).filter(MistakeModel.user_id == user_id)
        if owner_user_id is not None:
            query = query.filter(MistakeModel.owner_user_id == owner_user_id)
        return query.order_by(MistakeModel.occurrence_count.desc(), MistakeModel.last_seen_at.desc()).limit(limit).all()

    def resolve_mistake(self, mistake_id: str, user_id: str | None = None, owner_user_id: str | None = None) -> MistakeModel | None:
        query = self.db.query(MistakeModel).filter(MistakeModel.id == mistake_id)
        if user_id is not None:
            query = query.filter(MistakeModel.user_id == user_id)
        if owner_user_id is not None:
            query = query.filter(MistakeModel.owner_user_id == owner_user_id)
        mistake = query.first()
        if mistake:
            mistake.resolved = True
            self.db.commit()
            self.db.refresh(mistake)
        return mistake

    def review_mistake(self, mistake_id: str, user_id: str, owner_user_id: str, success: bool) -> MistakeModel | None:
        mistake = self.resolve_mistake(mistake_id, user_id, owner_user_id)
        if not mistake:
            return None
        now = datetime.now(timezone.utc)
        mistake.last_reviewed_at = now
        if success:
            mistake.successful_reuse_count = (mistake.successful_reuse_count or 0) + 1
            mistake.mastery_state = "mastered" if mistake.successful_reuse_count >= 3 else "reinforcing"
            mistake.resolved = mistake.mastery_state == "mastered"
            interval_days = 7 if mistake.resolved else 2
            mistake.next_review_at = now + timedelta(days=interval_days)
        else:
            mistake.mastery_state = "learning"
            mistake.resolved = False
            mistake.next_review_at = now + timedelta(hours=12)
        self.db.commit()
        self.db.refresh(mistake)
        return mistake
