from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.llm.router import get_model_router
from app.core.config import settings

router = APIRouter(prefix="/models", tags=["models"])

class ModelSelectRequest(BaseModel):
    preference: Optional[str] = None  # auto, local_only, cloud_only
    model: Optional[str] = None

@router.get("/")
@router.get("")
async def get_models():
    model_router = get_model_router()
    return await model_router.get_available_models()

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
async def select_model(req: ModelSelectRequest):
    """
    Dynamically update routing preference or active model in runtime.
    """
    if req.preference and req.preference in ["auto", "local_only", "cloud_only"]:
        settings.MODEL_ROUTING_PREFERENCE = req.preference
    if req.model:
        settings.OLLAMA_MODEL = req.model

    model_router = get_model_router()
    return {
        "status": "success",
        "routing_preference": settings.MODEL_ROUTING_PREFERENCE,
        "active_provider": await model_router.get_active_provider(),
        "ollama_model": settings.OLLAMA_MODEL
    }
