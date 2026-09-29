from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="")

@router.get("/health")
def health_check():
    return {"status": "ok", "model": settings.OLLAMA_MODEL}
