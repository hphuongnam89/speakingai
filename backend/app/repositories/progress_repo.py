from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.progress import DailyStatsModel
from app.models.session import SessionModel
from app.models.mistake import MistakeModel

class ProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_today(self, user_id: str = "default") -> DailyStatsModel:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        stat = self.db.query(DailyStatsModel).filter(
            DailyStatsModel.user_id == user_id,
            DailyStatsModel.date == today_str
        ).first()

        if not stat:
            stat = DailyStatsModel(
                user_id=user_id,
                date=today_str,
                speaking_minutes=0.0,
                session_count=0,
                word_count=0,
                avg_wpm=0.0,
                mistake_count=0
            )
            self.db.add(stat)
            self.db.commit()
            self.db.refresh(stat)
        return stat

    def record_activity(
        self,
        user_id: str = "default",
        speaking_minutes: float = 1.0,
        words: int = 50,
        mistakes: int = 0,
        band: float | None = None
    ):
        stat = self.get_or_create_today(user_id)
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

    def calculate_streak(self, user_id: str = "default") -> int:
        # Check consecutive days with activity
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        today_stat = self.db.query(DailyStatsModel).filter(
            DailyStatsModel.user_id == user_id,
            DailyStatsModel.date == today_str,
            DailyStatsModel.session_count > 0
        ).first()

        yesterday_stat = self.db.query(DailyStatsModel).filter(
            DailyStatsModel.user_id == user_id,
            DailyStatsModel.date == yesterday_str,
            DailyStatsModel.session_count > 0
        ).first()

        if not today_stat and not yesterday_stat:
            return 0

        # Count backwards
        streak = 1 if today_stat else 0
        start_day = 1 if today_stat else 1

        for i in range(1, 60):
            target_date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            s = self.db.query(DailyStatsModel).filter(
                DailyStatsModel.user_id == user_id,
                DailyStatsModel.date == target_date,
                DailyStatsModel.session_count > 0
            ).first()
            if s:
                streak += 1
            else:
                break
        return max(streak, 1)

    def get_weekly_stats(self, user_id: str = "default") -> list[dict]:
        now = datetime.now(timezone.utc)
        results = []

        # Return past 7 days (including today)
        for i in range(6, -1, -1):
            day_dt = now - timedelta(days=i)
            date_str = day_dt.strftime("%Y-%m-%d")
            day_name = day_dt.strftime("%a") # Mon, Tue, etc.

            stat = self.db.query(DailyStatsModel).filter(
                DailyStatsModel.user_id == user_id,
                DailyStatsModel.date == date_str
            ).first()

            results.append({
                "date": date_str,
                "day_of_week": day_name,
                "speaking_minutes": stat.speaking_minutes if stat else 0.0,
                "session_count": stat.session_count if stat else 0,
                "mistake_count": stat.mistake_count if stat else 0
            })
        return results

    def get_summary(self, user_id: str = "default") -> dict:
        streak = self.calculate_streak(user_id)

        # Aggregate total minutes & sessions from daily_stats or sessions table
        total_mins = self.db.query(func.sum(DailyStatsModel.speaking_minutes)).filter(
            DailyStatsModel.user_id == user_id
        ).scalar() or 0.0

        total_sessions = self.db.query(func.sum(DailyStatsModel.session_count)).filter(
            DailyStatsModel.user_id == user_id
        ).scalar() or 0

        total_words = self.db.query(func.sum(DailyStatsModel.word_count)).filter(
            DailyStatsModel.user_id == user_id
        ).scalar() or 0

        avg_wpm = round(total_words / max(total_mins, 1.0), 1) if total_mins > 0 else 110.0

        # Latest band score
        latest_session_with_band = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.estimated_band.isnot(None)
        ).order_by(SessionModel.started_at.desc()).first()

        latest_band = latest_session_with_band.estimated_band if latest_session_with_band else None
        if latest_band is None:
            latest_stat_with_band = self.db.query(DailyStatsModel).filter(
                DailyStatsModel.user_id == user_id,
                DailyStatsModel.estimated_band.isnot(None)
            ).order_by(DailyStatsModel.date.desc()).first()
            if latest_stat_with_band:
                latest_band = latest_stat_with_band.estimated_band

        # Total unresolved mistakes
        total_mistakes = self.db.query(MistakeModel).filter(
            MistakeModel.user_id == user_id,
            MistakeModel.resolved == False
        ).count()

        return {
            "streak": max(streak, 1),
            "total_speaking_minutes": round(float(total_mins), 1),
            "total_sessions": int(total_sessions),
            "avg_wpm": float(avg_wpm),
            "latest_band": float(latest_band) if latest_band else None,
            "total_mistakes": int(total_mistakes)
        }
