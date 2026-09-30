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
        self.request_counter = 0
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

        client_ip = request.headers.get("x-real-ip") or (request.client.host if request.client else "unknown")
        is_auth_endpoint = path in {"/api/v1/auth/login", "/api/v1/auth/register"}
        bucket_key = f"{client_ip}:auth" if is_auth_endpoint else client_ip
        request_limit = min(settings.RATE_LIMIT_PER_MINUTE, 10) if is_auth_endpoint else settings.RATE_LIMIT_PER_MINUTE
        now = time.time()

        with self.lock:
            # Clean expired timestamps for this IP
            cutoff = now - self.window_seconds
            self.request_counter += 1
            if self.request_counter % 256 == 0 or len(self.requests) >= 10000:
                self.requests = {
                    ip: [timestamp for timestamp in timestamps if timestamp > cutoff]
                    for ip, timestamps in self.requests.items()
                    if any(timestamp > cutoff for timestamp in timestamps)
                }
            ip_requests = [t for t in self.requests.get(bucket_key, []) if t > cutoff]

            if len(ip_requests) >= request_limit:
                oldest = ip_requests[0]
                retry_after = int(self.window_seconds - (now - oldest)) + 1
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Rate limit exceeded: Maximum {request_limit} requests per minute",
                        "retry_after_seconds": max(1, retry_after)
                    },
                    headers={"Retry-After": str(max(1, retry_after))}
                )

            ip_requests.append(now)
            self.requests[bucket_key] = ip_requests

        return await call_next(request)
