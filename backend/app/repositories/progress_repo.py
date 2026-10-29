from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.progress import DailyStatsModel
from app.models.session import SessionModel
from app.models.mistake import MistakeModel


class ProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def _owned(self, query, model, owner_user_id: str | None):
        return query.filter(model.owner_user_id == owner_user_id) if owner_user_id is not None else query

    def get_or_create_today(self, user_id: str = "default", owner_user_id: str | None = None) -> DailyStatsModel:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        query = self.db.query(DailyStatsModel).filter(
            DailyStatsModel.user_id == user_id,
            DailyStatsModel.date == today_str,
        )
        query = self._owned(query, DailyStatsModel, owner_user_id)
        stat = query.first()
        if not stat:
            stat = DailyStatsModel(
                user_id=user_id,
                owner_user_id=owner_user_id or "default",
                date=today_str,
                speaking_minutes=0.0,
                session_count=0,
                word_count=0,
                avg_wpm=0.0,
                mistake_count=0,
            )
            self.db.add(stat)
            self.db.commit()
            self.db.refresh(stat)
        return stat

    def record_activity(self, user_id: str = "default", speaking_minutes: float = 1.0, words: int = 50, mistakes: int = 0, band: float | None = None, owner_user_id: str | None = None):
        stat = self.get_or_create_today(user_id, owner_user_id)
        stat.session_count += 1
        stat.speaking_minutes += max(0.5, round(speaking_minutes, 1))
        stat.word_count += words
        stat.mistake_count += mistakes
        if stat.speaking_minutes > 0:
            stat.avg_wpm = round(stat.word_count / stat.speaking_minutes, 1)
        if band:
            stat.estimated_band = band
        self.db.commit()
        self.db.refresh(stat)
        return stat

    def calculate_streak(self, user_id: str = "default", owner_user_id: str | None = None) -> int:
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        def active_on(date_str: str):
            query = self.db.query(DailyStatsModel).filter(
                DailyStatsModel.user_id == user_id,
                DailyStatsModel.date == date_str,
                DailyStatsModel.session_count > 0,
            )
            return self._owned(query, DailyStatsModel, owner_user_id).first()

        today_stat = active_on(today_str)
        yesterday_stat = active_on(yesterday_str)
        if not today_stat and not yesterday_stat:
            return 0
        streak = 1 if today_stat else 0
        for i in range(1, 60):
            target_date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            if active_on(target_date):
                streak += 1
            else:
                break
        return max(streak, 1)

    def get_weekly_stats(self, user_id: str = "default", owner_user_id: str | None = None) -> list[dict]:
        now = datetime.now(timezone.utc)
        results = []
        for i in range(6, -1, -1):
            day_dt = now - timedelta(days=i)
            date_str = day_dt.strftime("%Y-%m-%d")
            query = self.db.query(DailyStatsModel).filter(
                DailyStatsModel.user_id == user_id,
                DailyStatsModel.date == date_str,
            )
            stat = self._owned(query, DailyStatsModel, owner_user_id).first()
            results.append({
                "date": date_str,
                "day_of_week": day_dt.strftime("%a"),
                "speaking_minutes": stat.speaking_minutes if stat else 0.0,
                "session_count": stat.session_count if stat else 0,
                "mistake_count": stat.mistake_count if stat else 0,
            })
        return results

    def get_summary(self, user_id: str = "default", owner_user_id: str | None = None) -> dict:
        streak = self.calculate_streak(user_id, owner_user_id)
        stat_query = self.db.query(DailyStatsModel)
        stat_query = stat_query.filter(DailyStatsModel.user_id == user_id)
        stat_query = self._owned(stat_query, DailyStatsModel, owner_user_id)
        total_mins = stat_query.with_entities(func.sum(DailyStatsModel.speaking_minutes)).scalar() or 0.0
        total_sessions = stat_query.with_entities(func.sum(DailyStatsModel.session_count)).scalar() or 0
        total_words = stat_query.with_entities(func.sum(DailyStatsModel.word_count)).scalar() or 0
        avg_wpm = round(total_words / max(total_mins, 1.0), 1) if total_mins > 0 else 110.0

        session_query = self.db.query(SessionModel).filter(SessionModel.user_id == user_id, SessionModel.estimated_band.isnot(None))
        session_query = self._owned(session_query, SessionModel, owner_user_id)
        latest_session_with_band = session_query.order_by(SessionModel.started_at.desc()).first()
        latest_band = latest_session_with_band.estimated_band if latest_session_with_band else None
        band_query = self.db.query(DailyStatsModel).filter(DailyStatsModel.user_id == user_id, DailyStatsModel.estimated_band.isnot(None))
        band_query = self._owned(band_query, DailyStatsModel, owner_user_id)
        latest_stat_with_band = band_query.order_by(DailyStatsModel.date.desc()).first()
        if latest_band is None and latest_stat_with_band:
            latest_band = latest_stat_with_band.estimated_band

        mistake_query = self.db.query(MistakeModel).filter(MistakeModel.user_id == user_id, MistakeModel.resolved == False)
        mistake_query = self._owned(mistake_query, MistakeModel, owner_user_id)
        return {
            "streak": max(streak, 1),
            "total_speaking_minutes": round(float(total_mins), 1),
            "total_sessions": int(total_sessions),
            "avg_wpm": float(avg_wpm),
            "latest_band": float(latest_band) if latest_band else None,
            "total_mistakes": int(mistake_query.count()),
        }
