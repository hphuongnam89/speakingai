import os
from datetime import datetime, timezone
from app.core.database import SessionLocal
from app.models.audio import AudioRecordingModel


def cleanup_expired_audio() -> int:
    removed = 0
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        records = db.query(AudioRecordingModel).filter(AudioRecordingModel.retention_at <= now).all()
        for record in records:
            try:
                os.remove(record.file_path)
            except OSError:
                pass
            db.delete(record)
            removed += 1
        db.commit()
    return removed
