import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.auth import verify_api_key
from app.core.rate_limit import RateLimitMiddleware
from app.core.security import SecurityHeadersMiddleware
from app.core.telemetry import RequestTracingMiddleware
from app.api import (
    health,
    sessions,
    speech,
    conversation,
    models,
    mistakes,
    settings as api_settings,
    ielts,
    progress,
    pronunciation
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Database migration & directory creation
    init_db()
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    yield
    # Shutdown logic (if any)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="IELTS Speaking AI Coach — Cloud & Production Backend",
    lifespan=lifespan
)

# Parse CORS Origins
if settings.CORS_ORIGINS == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

# Register Middlewares in proper order (outermost to innermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestTracingMiddleware)

# Public Endpoints (No API key required)
app.include_router(health.router, prefix="/api/v1")

# Protected Endpoints (Requires API key if API_KEY_ENABLED=True)
protected_deps = [Depends(verify_api_key)]
app.include_router(sessions.router, prefix="/api/v1", dependencies=protected_deps)
app.include_router(speech.router, prefix="/api/v1", dependencies=protected_deps)
app.include_router(conversation.router, prefix="/api/v1", dependencies=protected_deps)
app.include_router(models.router, prefix="/api/v1", dependencies=protected_deps)
app.include_router(mistakes.router, prefix="/api/v1", dependencies=protected_deps)
app.include_router(api_settings.router, prefix="/api/v1", dependencies=protected_deps)
app.include_router(ielts.router, prefix="/api/v1", dependencies=protected_deps)
app.include_router(progress.router, prefix="/api/v1", dependencies=protected_deps)
app.include_router(pronunciation.router, prefix="/api/v1", dependencies=protected_deps)

@app.get("/")
def read_root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "environment": settings.ENVIRONMENT,
        "auth_enabled": settings.API_KEY_ENABLED,
        "rate_limiting": settings.RATE_LIMIT_ENABLED
    }
