import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.profile import ProfileModel
from app.models.session import SessionModel
from app.models.turn import TurnModel
from app.models.mistake import MistakeModel
from app.models.progress import DailyStatsModel
from app.models.audio import AudioRecordingModel


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self, owner_user_id: str | None = None) -> List[ProfileModel]:
        query = self.db.query(ProfileModel)
        if owner_user_id is not None:
            query = query.filter(ProfileModel.owner_user_id == owner_user_id)
        return query.order_by(ProfileModel.last_active_at.desc()).all()

    def get(self, profile_id: str, owner_user_id: str | None = None) -> Optional[ProfileModel]:
        query = self.db.query(ProfileModel).filter(ProfileModel.id == profile_id)
        if owner_user_id is not None:
            query = query.filter(ProfileModel.owner_user_id == owner_user_id)
        return query.first()

    def get_active(self, owner_user_id: str | None = None) -> Optional[ProfileModel]:
        query = self.db.query(ProfileModel).filter(ProfileModel.is_active == True)
        if owner_user_id is not None:
            query = query.filter(ProfileModel.owner_user_id == owner_user_id)
        active = query.first()
        if not active:
            # Fallback to the most recently active profile
            query = self.db.query(ProfileModel)
            if owner_user_id is not None:
                query = query.filter(ProfileModel.owner_user_id == owner_user_id)
            active = query.order_by(ProfileModel.last_active_at.desc()).first()
            if active:
                active.is_active = True
                self.db.commit()
                self.db.refresh(active)
        return active

    def set_active(self, profile_id: str, owner_user_id: str | None = None) -> Optional[ProfileModel]:
        target = self.get(profile_id, owner_user_id)
        if not target:
            return None

        # Deactivate only profiles owned by this principal
        self.db.query(ProfileModel).filter(ProfileModel.owner_user_id == (owner_user_id or target.owner_user_id)).update({ProfileModel.is_active: False})
        target.is_active = True
        target.last_active_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(target)
        return target

    def create(
        self,
        name: str,
        target_band: float = 7.0,
        daily_target_minutes: int = 20,
        target_duration_months: int = 3,
        avatar_color: str = "#4f46e5",
        owner_user_id: str = "default"
    ) -> ProfileModel:
        # Deactivate current active profile for this owner only
        self.db.query(ProfileModel).filter(ProfileModel.owner_user_id == owner_user_id).update({ProfileModel.is_active: False})

        profile = ProfileModel(
            id=str(uuid.uuid4()),
            name=name.strip(),
            owner_user_id=owner_user_id,
            avatar_color=avatar_color,
            current_band=None,
            target_band=target_band,
            daily_target_minutes=daily_target_minutes,
            target_duration_months=target_duration_months,
            placement_status="not_started",
            roadmap_data=None,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            last_active_at=datetime.now(timezone.utc)
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update_placement_result(
        self,
        profile_id: str,
        current_band: float,
        roadmap_data: Dict[str, Any],
        owner_user_id: str | None = None
    ) -> Optional[ProfileModel]:
        profile = self.get(profile_id, owner_user_id)
        if not profile:
            return None

        profile.current_band = current_band
        profile.placement_status = "completed"
        profile.roadmap_data = json.dumps(roadmap_data, ensure_ascii=False)
        profile.last_active_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete(self, profile_id: str, owner_user_id: str | None = None) -> bool:
        profile = self.get(profile_id, owner_user_id)
        if not profile:
            return False

        # Find all sessions of this profile
        session_query = self.db.query(SessionModel).filter(SessionModel.user_id == profile_id)
        if owner_user_id is not None:
            session_query = session_query.filter(SessionModel.owner_user_id == owner_user_id)
        sessions = session_query.all()
        session_ids = [s.id for s in sessions]

        # Clean up audio recordings on disk and database
        if session_ids:
            audio_query = self.db.query(AudioRecordingModel).filter(AudioRecordingModel.session_id.in_(session_ids))
            if owner_user_id is not None:
                audio_query = audio_query.filter(AudioRecordingModel.owner_user_id == owner_user_id)
            recordings = audio_query.all()
            for rec in recordings:
                try:
                    os.remove(rec.file_path)
                except OSError:
                    pass
            audio_query.delete(synchronize_session=False)

            # Delete turns
            turn_query = self.db.query(TurnModel).filter(TurnModel.session_id.in_(session_ids))
            if owner_user_id is not None:
                turn_query = turn_query.filter(TurnModel.owner_user_id == owner_user_id)
            turn_query.delete(synchronize_session=False)

            # Delete sessions
            session_query.delete(synchronize_session=False)

        # Delete mistakes
        mistake_query = self.db.query(MistakeModel).filter(MistakeModel.user_id == profile_id)
        if owner_user_id is not None:
            mistake_query = mistake_query.filter(MistakeModel.owner_user_id == owner_user_id)
        mistake_query.delete(synchronize_session=False)

        # Delete daily stats
        stats_query = self.db.query(DailyStatsModel).filter(DailyStatsModel.user_id == profile_id)
        if owner_user_id is not None:
            stats_query = stats_query.filter(DailyStatsModel.owner_user_id == owner_user_id)
        stats_query.delete(synchronize_session=False)

        self.db.delete(profile)
        self.db.commit()
        return True
