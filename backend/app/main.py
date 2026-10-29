import os
import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.core.auth import verify_api_key
from app.core.rate_limit import RateLimitMiddleware
from app.core.security import SecurityHeadersMiddleware
from app.core.telemetry import RequestTracingMiddleware

if settings.SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        send_default_pii=False,
        max_request_body_size="never",
        traces_sample_rate=0.0,
    )
from app.api import (
    auth,
    health,
    sessions,
    speech,
    conversation,
    models,
    mistakes,
    settings as api_settings,
    ielts,
    progress,
    pronunciation,
    profiles,
    placement,
    pilot
)

logger = logging.getLogger(__name__)

async def periodic_audio_cleanup():
    from app.services.audio_retention import cleanup_expired_audio
    while True:
        try:
            await asyncio.sleep(3600)  # Chạy dọn dẹp mỗi 1 giờ
            removed = cleanup_expired_audio()
            if removed > 0:
                logger.info(f"Periodic audio cleanup removed {removed} expired recordings")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during periodic audio cleanup: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Database migration & directory creation
    init_db()
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    from app.services.audio_retention import cleanup_expired_audio
    cleanup_expired_audio()
    cleanup_task = asyncio.create_task(periodic_audio_cleanup())
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="IELTS Speaking AI Coach — Cloud & Production Backend",
    docs_url=None if settings.ENVIRONMENT.lower() == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT.lower() == "production" else "/redoc",
    openapi_url=None if settings.ENVIRONMENT.lower() == "production" else "/openapi.json",
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
    allow_credentials=settings.CORS_ORIGINS.strip() != "*",
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestTracingMiddleware)

# Public Endpoints (No API key required)
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

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
app.include_router(profiles.router, prefix="/api/v1", dependencies=protected_deps)
app.include_router(placement.router, prefix="/api/v1", dependencies=protected_deps)
app.include_router(pilot.router, prefix="/api/v1", dependencies=protected_deps)

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
app.mount("/static", StaticFiles(directory=WEB_DIR), name="web-static")

@app.get("/", include_in_schema=False)
def web_home():
    if settings.ENVIRONMENT.strip().lower() == "production":
        return read_root()
    return FileResponse(WEB_DIR / "index.html")

@app.get("/api/v1/info")
def read_root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": None if settings.ENVIRONMENT.lower() == "production" else "/docs",
        "environment": settings.ENVIRONMENT,
        "auth_enabled": settings.API_KEY_ENABLED,
        "rate_limiting": settings.RATE_LIMIT_ENABLED
    }
