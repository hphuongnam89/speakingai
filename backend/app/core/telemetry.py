import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("api.telemetry")

class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Assigns or preserves X-Request-ID and logs latency and status for observability.
    """
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id

        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = round((time.time() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Process-Time-Ms"] = str(process_time)
            
            # Log non-health requests
            if not request.url.path.startswith("/api/v1/health") and not request.url.path.startswith("/docs"):
                logger.info(
                    f"[{req_id}] {request.method} {request.url.path} -> {response.status_code} ({process_time}ms)"
                )
            return response
        except Exception as exc:
            process_time = round((time.time() - start_time) * 1000, 2)
            logger.error(
                f"[{req_id}] UNHANDLED ERROR in {request.method} {request.url.path}: {exc} ({process_time}ms)",
                exc_info=True
            )
            raise exc
