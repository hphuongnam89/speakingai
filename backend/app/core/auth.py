import logging
from typing import Optional
from fastapi import Request, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)

def verify_api_key(
    request: Request,
    api_key: Optional[str] = Security(api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(http_bearer)
) -> bool:
    """
    Validates backend API Key when API_KEY_ENABLED is True.
    Supports either 'X-API-Key' header or 'Authorization: Bearer <token>'.
    If API_KEY_ENABLED is False (local LAN default), access is granted unconditionally.
    """
    if not settings.API_KEY_ENABLED:
        return True

    provided_key = api_key or (bearer.credentials if bearer else None)

    if not provided_key or provided_key != settings.API_KEY:
        logger.warning(f"Unauthorized API access attempt from {request.client.host if request.client else 'unknown'}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Missing or invalid API Key",
            headers={"WWW-Authenticate": "ApiKey or Bearer"}
        )
    return True

def get_current_user_id(request: Request) -> str:
    """
    Extracts user_id from 'X-User-Id' header if present, fallback to 'default'.
    Ensures multi-user synchronization readiness.
    """
    user_id = request.headers.get("X-User-Id")
    if user_id and user_id.strip():
        return user_id.strip()
    return "default"
