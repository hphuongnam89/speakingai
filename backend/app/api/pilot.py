from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.auth import get_current_principal_id
from app.core.database import get_db
from app.models.pilot import PilotRunModel, PilotEventModel, PilotFeedbackModel
from app.schemas.pilot import (
    PilotStartRequest, PilotStartResponse, PilotEventRequest,
    PilotFeedbackRequest, PilotSummaryResponse,
)

router = APIRouter(prefix="/pilot", tags=["pilot"])
ALLOWED_OUTCOMES = {"completed_without_help", "completed_with_help", "blocked"}


def get_owned_run(run_id: str, request: Request, db: Session) -> PilotRunModel:
    run = db.query(PilotRunModel).filter(
        PilotRunModel.id == run_id,
        PilotRunModel.owner_user_id == get_current_principal_id(request),
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail="Pilot run not found")
    return run


@router.post("/runs", response_model=PilotStartResponse)
def start_pilot(request_data: PilotStartRequest, request: Request, db: Session = Depends(get_db)):
    if not request_data.consent_feedback:
        raise HTTPException(status_code=400, detail="Pilot feedback consent is required")
    run = PilotRunModel(
        owner_user_id=get_current_principal_id(request),
        participant_code=request_data.participant_code,
        consent_audio=request_data.consent_audio,
        consent_feedback=request_data.consent_feedback,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return PilotStartResponse(
        pilot_run_id=run.id,
        status=run.status,
        audio_recording_allowed=run.consent_audio,
    )


@router.post("/runs/{run_id}/events")
def record_pilot_event(run_id: str, data: PilotEventRequest, request: Request, db: Session = Depends(get_db)):
    run = get_owned_run(run_id, request, db)
    if run.status != "active":
        raise HTTPException(status_code=409, detail="Pilot run is no longer active")
    if data.outcome not in ALLOWED_OUTCOMES:
        raise HTTPException(status_code=422, detail="Unsupported pilot outcome")
    if data.outcome != "blocked" and not data.help_used and data.understood_quote:
        data.understood_quote = None
    db.add(PilotEventModel(
        pilot_run_id=run.id,
        owner_user_id=run.owner_user_id,
        task_key=data.task_key,
        outcome=data.outcome,
        help_used=data.help_used,
        understood_quote=data.understood_quote,
    ))
    db.commit()
    return {"status": "recorded"}


@router.post("/runs/{run_id}/feedback")
def submit_pilot_feedback(run_id: str, data: PilotFeedbackRequest, request: Request, db: Session = Depends(get_db)):
    run = get_owned_run(run_id, request, db)
    if not run.consent_feedback:
        raise HTTPException(status_code=403, detail="Pilot feedback consent is missing")
    feedback = db.query(PilotFeedbackModel).filter(PilotFeedbackModel.pilot_run_id == run.id).first()
    if feedback:
        raise HTTPException(status_code=409, detail="Pilot feedback already submitted")
    db.add(PilotFeedbackModel(
        pilot_run_id=run.id,
        owner_user_id=run.owner_user_id,
        next_action_clear=data.next_action_clear,
        correction_useful=data.correction_useful,
        score_too_certain=data.score_too_certain,
        would_return=data.would_return,
        free_text=data.free_text,
    ))
    run.status = "completed"
    run.completed_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "recorded"}


@router.get("/runs/{run_id}/summary", response_model=PilotSummaryResponse)
def get_pilot_summary(run_id: str, request: Request, db: Session = Depends(get_db)):
    run = get_owned_run(run_id, request, db)
    events = db.query(PilotEventModel).filter(PilotEventModel.pilot_run_id == run.id).all()
    counts = {outcome: sum(1 for event in events if event.outcome == outcome) for outcome in ALLOWED_OUTCOMES}
    denominator = len(events)
    completed = counts["completed_without_help"] + counts["completed_with_help"]
    feedback = db.query(PilotFeedbackModel).filter(PilotFeedbackModel.pilot_run_id == run.id).first()
    return PilotSummaryResponse(
        pilot_run_id=run.id,
        event_count=denominator,
        completed_without_help=counts["completed_without_help"],
        completed_with_help=counts["completed_with_help"],
        blocked=counts["blocked"],
        completion_rate=round(completed / denominator, 2) if denominator else 0.0,
        feedback_submitted=feedback is not None,
    )


@router.delete("/runs/{run_id}")
def delete_pilot_run(run_id: str, request: Request, db: Session = Depends(get_db)):
    run = get_owned_run(run_id, request, db)
    db.query(PilotEventModel).filter(PilotEventModel.pilot_run_id == run.id).delete(synchronize_session=False)
    db.query(PilotFeedbackModel).filter(PilotFeedbackModel.pilot_run_id == run.id).delete(synchronize_session=False)
    db.delete(run)
    db.commit()
    return {"status": "deleted"}
