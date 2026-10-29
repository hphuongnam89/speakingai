import json
import os
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.profile import ProfileModel
from app.models.session import SessionModel
from app.repositories.profile_repo import ProfileRepository
from app.repositories.progress_repo import ProgressRepository
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.core.auth import get_current_principal_id

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _to_response(profile: ProfileModel, db: Session) -> ProfileResponse:
    progress_repo = ProgressRepository(db)
    today_stat = progress_repo.get_or_create_today(profile.id)
    streak = progress_repo.calculate_streak(profile.id)
    total_sessions = db.query(SessionModel).filter(SessionModel.user_id == profile.id).count()

    roadmap = None
    if profile.roadmap_data:
        try:
            roadmap = json.loads(profile.roadmap_data)
        except Exception:
            roadmap = None

    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        avatar_color=profile.avatar_color or "#4f46e5",
        current_band=profile.current_band,
        target_band=profile.target_band,
        daily_target_minutes=profile.daily_target_minutes,
        target_duration_months=profile.target_duration_months,
        placement_status=profile.placement_status,
        roadmap_data=roadmap,
        is_active=profile.is_active,
        today_speaking_minutes=round(today_stat.speaking_minutes, 1) if today_stat else 0.0,
        streak_days=streak,
        total_sessions=total_sessions,
        created_at=profile.created_at,
        last_active_at=profile.last_active_at
    )


@router.get("", response_model=List[ProfileResponse])
@router.get("/", response_model=List[ProfileResponse])
def list_profiles(request: Request, db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    profiles = repo.list_all(get_current_principal_id(request))
    return [_to_response(p, db) for p in profiles]


@router.post("/reset-all")
def reset_all_data(request: Request, db: Session = Depends(get_db)):
    """
    Clears all local user profiles, sessions, turns, mistakes, and progress stats
    to start completely fresh from scratch.
    """
    from app.models import TurnModel, MistakeModel, DailyStatsModel, AudioRecordingModel
    owner = get_current_principal_id(request)
    profiles = db.query(ProfileModel).filter(ProfileModel.owner_user_id == owner).all()
    profile_ids = [p.id for p in profiles]
    sessions = db.query(SessionModel).filter(SessionModel.owner_user_id == owner).all()
    session_ids = [s.id for s in sessions]
    for recording in db.query(AudioRecordingModel).filter(AudioRecordingModel.owner_user_id == owner).all():
        try: os.remove(recording.file_path)
        except OSError: pass
    db.query(TurnModel).filter(TurnModel.owner_user_id == owner).delete(synchronize_session=False)
    db.query(SessionModel).filter(SessionModel.owner_user_id == owner).delete(synchronize_session=False)
    db.query(MistakeModel).filter(MistakeModel.owner_user_id == owner).delete(synchronize_session=False)
    db.query(DailyStatsModel).filter(DailyStatsModel.owner_user_id == owner).delete(synchronize_session=False)
    db.query(AudioRecordingModel).filter(AudioRecordingModel.owner_user_id == owner).delete(synchronize_session=False)
    db.query(ProfileModel).filter(ProfileModel.owner_user_id == owner).delete(synchronize_session=False)
    db.commit()
    return {"status": "success", "message": "All local data reset successfully"}


@router.post("", response_model=ProfileResponse)
@router.post("/", response_model=ProfileResponse)
def create_profile(data: ProfileCreate, request: Request, db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    profile = repo.create(
        name=data.name,
        target_band=data.target_band,
        daily_target_minutes=data.daily_target_minutes,
        target_duration_months=data.target_duration_months,
        avatar_color=data.avatar_color or "#4f46e5",
        owner_user_id=get_current_principal_id(request)
    )
    return _to_response(profile, db)


@router.get("/active", response_model=Optional[ProfileResponse])
def get_active_profile(request: Request, db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    active = repo.get_active(get_current_principal_id(request))
    if not active:
        return None
    return _to_response(active, db)


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: str, request: Request, db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    profile = repo.get(profile_id, get_current_principal_id(request))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_response(profile, db)


@router.post("/{profile_id}/select", response_model=ProfileResponse)
def select_profile(profile_id: str, request: Request, db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    profile = repo.set_active(profile_id, get_current_principal_id(request))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_response(profile, db)


logger = logging.getLogger(__name__)


@router.put("/{profile_id}", response_model=ProfileResponse)
def update_profile(profile_id: str, data: ProfileUpdate, request: Request, db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    profile = repo.get(profile_id, get_current_principal_id(request))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if data.name is not None and data.name.strip():
        profile.name = data.name.strip()
    if data.target_band is not None:
        profile.target_band = data.target_band
    if data.daily_target_minutes is not None:
        profile.daily_target_minutes = data.daily_target_minutes
    if data.target_duration_months is not None:
        profile.target_duration_months = data.target_duration_months
    if data.roadmap_data is not None:
        profile.roadmap_data = json.dumps(data.roadmap_data, ensure_ascii=False)

    db.commit()
    db.refresh(profile)
    return _to_response(profile, db)


@router.post("/{profile_id}/roadmap/recalculate", response_model=ProfileResponse)
async def recalculate_roadmap(profile_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Recalculates a personalized 3-phase roadmap based on the profile's current band,
    target band, daily minutes, and target duration months.
    """
    repo = ProfileRepository(db)
    profile = repo.get(profile_id, get_current_principal_id(request))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    current_b = profile.current_band if profile.current_band is not None else 4.5
    target_b = profile.target_band or 7.0
    daily_m = profile.daily_target_minutes or 20
    dur_m = profile.target_duration_months or 3
    total_hours = round((daily_m / 60.0) * (dur_m * 30), 1)

    # Calculate step bands
    step = (target_b - current_b) / 3.0
    p1_band = round(current_b + max(0.5, step), 1)
    p2_band = round(current_b + max(1.0, step * 2), 1)
    if p2_band >= target_b:
        p2_band = round(target_b - 0.5, 1)

    new_roadmap = {
        "total_hours": total_hours,
        "feasibility": f"Rất khả thi nếu học viên duy trì đều đặn {daily_m} phút mỗi ngày trong {dur_m} tháng.",
        "phases": [
            {
                "phase_name": f"Giai đoạn 1: Chuẩn hóa phát âm & Phản xạ câu đơn/kép",
                "target_band": min(p1_band, target_b),
                "focus_areas": [
                    "Xóa triệt để lỗi ngữ pháp thì quá khứ và chia động từ số ít/nhiều",
                    f"Rèn luyện phản xạ nói tiếng Anh {daily_m} phút mỗi ngày cùng AI Coach",
                    "Mở rộng câu trả lời Part 1 theo công thức: Idea -> Reason -> Example"
                ]
            },
            {
                "phase_name": f"Giai đoạn 2: Tăng tốc làm chủ Part 2 (Nói 2 phút tự tin)",
                "target_band": min(p2_band, target_b),
                "focus_areas": [
                    "Nói liên tục 2 phút không ngắc ngứ với cấu trúc Mind-map 4 câu hỏi gợi ý",
                    "Bổ sung vốn Collocations và Idiomatic expressions B2/C1 tự nhiên",
                    "Kiểm soát ngữ điệu và giảm các khoảng ngừng ngập ngừng 'um, uh, like'"
                ]
            },
            {
                "phase_name": f"Giai đoạn 3: Tư duy phản biện Part 3 & Cán mốc Band {target_b}",
                "target_band": target_b,
                "focus_areas": [
                    "Tư duy phản biện 2 chiều cho các câu hỏi trừu tượng (công nghệ, xã hội, giáo dục)",
                    "Mô phỏng áp lực phòng thi 15 phút cùng giám khảo AI local",
                    "Tối ưu độ chính xác từ vựng và tự tin trả lời lưu loát ở tốc độ cao"
                ]
            }
        ]
    }

    # If existing roadmap_data had weaknesses, preserve them
    existing_data = {}
    if profile.roadmap_data:
        try:
            existing_data = json.loads(profile.roadmap_data)
        except Exception:
            pass

    existing_data["roadmap"] = new_roadmap
    profile.roadmap_data = json.dumps(existing_data, ensure_ascii=False)
    db.commit()
    db.refresh(profile)
    return _to_response(profile, db)


@router.post("/{profile_id}/placement/reset", response_model=ProfileResponse)
def reset_profile_placement(profile_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Resets the placement test for this profile, allowing them to retake the diagnostic test.
    """
    repo = ProfileRepository(db)
    profile = repo.get(profile_id, get_current_principal_id(request))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.placement_status = "not_started"
    profile.current_band = None
    profile.roadmap_data = None
    db.commit()
    db.refresh(profile)
    return _to_response(profile, db)


@router.delete("/{profile_id}")
def delete_profile(profile_id: str, request: Request, db: Session = Depends(get_db)):
    repo = ProfileRepository(db)
    owner = get_current_principal_id(request)
    all_profiles = repo.list_all(owner)
    if len(all_profiles) <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the only existing profile.")

    success = repo.delete(profile_id, owner)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Set another active profile if active was deleted
    active = repo.get_active(owner)
    return {"status": "success", "active_profile_id": active.id if active else None}

