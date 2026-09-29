import time
import threading
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory Sliding Window Rate Limiter.
    Limits requests per client IP within a 60-second rolling window.
    """
    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, List[float]] = {}
        self.lock = threading.Lock()
        self.window_seconds = 60
        self.whitelist_prefixes = [
            "/docs",
            "/openapi.json",
            "/redoc",
            "/api/v1/health",
            "/favicon.ico"
        ]

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        path = request.url.path
        if any(path.startswith(prefix) for prefix in self.whitelist_prefixes) or path == "/":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        with self.lock:
            # Clean expired timestamps for this IP
            cutoff = now - self.window_seconds
            ip_requests = [t for t in self.requests.get(client_ip, []) if t > cutoff]

            if len(ip_requests) >= settings.RATE_LIMIT_PER_MINUTE:
                oldest = ip_requests[0]
                retry_after = int(self.window_seconds - (now - oldest)) + 1
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Rate limit exceeded: Maximum {settings.RATE_LIMIT_PER_MINUTE} requests per minute",
                        "retry_after_seconds": max(1, retry_after)
                    },
                    headers={"Retry-After": str(max(1, retry_after))}
                )

            ip_requests.append(now)
            self.requests[client_ip] = ip_requests

        return await call_next(request)
