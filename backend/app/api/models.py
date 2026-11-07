from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.llm.router import get_model_router
from app.core.config import settings
from app.core.auth import get_current_user_id
from app.core.database import get_db
from app.repositories.settings_repo import SettingsRepository
from sqlalchemy.orm import Session

router = APIRouter(prefix="/models", tags=["models"])

class ModelSelectRequest(BaseModel):
    preference: Optional[str] = None  # auto, local_only, cloud_only
    model: Optional[str] = None

@router.get("/")
@router.get("")
async def get_models(request: Request, db: Session = Depends(get_db)):
    model_router = get_model_router()
    result = await model_router.get_available_models()
    health = await model_router.ollama.test_connection()
    result["installed_models"] = health.get("installed_models", [])
    result["selected_model"] = SettingsRepository(db).get_or_create(get_current_user_id(request)).preferred_model or settings.OLLAMA_MODEL
    return result

@router.get("/status")
async def get_model_status():
    """
    Returns live health, latency, and status for both Local Ollama and Cloud DeepSeek providers.
    """
    model_router = get_model_router()
    return await model_router.check_providers_health()

@router.post("/test-connection")
async def test_connection():
    """
    Directly tests connectivity to both Ollama and DeepSeek and reports latency.
    """
    model_router = get_model_router()
    return await model_router.check_providers_health()

@router.post("/select")
async def select_model(req: ModelSelectRequest, request: Request, db: Session = Depends(get_db)):
    """
    Dynamically update routing preference or active model in runtime.
    """
    if req.preference and req.preference not in ["auto", "local_only", "cloud_only"]:
        raise HTTPException(status_code=422, detail="Invalid routing preference")
    if req.model:
        health = await get_model_router().ollama.test_connection()
        if req.model not in health.get("installed_models", []):
            raise HTTPException(status_code=422, detail="Select an installed model; no automatic download")
    selected = SettingsRepository(db).update(get_current_user_id(request),
        preferred_model=req.model, provider_preference=req.preference)

    model_router = get_model_router()
    return {
        "status": "success",
        "routing_preference": selected.provider_preference,
        "active_provider": await model_router.get_active_provider(),
        "ollama_model": selected.preferred_model or settings.OLLAMA_MODEL
    }
