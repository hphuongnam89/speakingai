from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.config import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applies security headers to prevent MIME confusion, clickjacking, and XSS.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if settings.ENABLE_SECURITY_HEADERS:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

def mask_secret(secret: str | None) -> str:
    """
    Masks sensitive secrets for safe display in logs and telemetry.
    e.g. "sk-1234567890abcdef" -> "sk-12****cdef"
    """
    if not secret:
        return ""
    if len(secret) <= 6:
        return "******"
    return f"{secret[:4]}****{secret[-4:]}"
