import logging
import hmac
import base64
import hashlib
import json
import secrets
import time
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
    if bearer:
        user_id = decode_access_token(bearer.credentials)
        if user_id:
            request.state.user_id = user_id
            return True
        if not api_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")

    provided_key = api_key or (bearer.credentials if bearer else None)

    if not settings.API_KEY_ENABLED:
        if bearer:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")
        request.state.user_id = "default"
        return True

    if not provided_key or not hmac.compare_digest(provided_key, settings.API_KEY):
        logger.warning(f"Unauthorized API access attempt from {request.client.host if request.client else 'unknown'}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Missing or invalid API Key",
            headers={"WWW-Authenticate": "ApiKey or Bearer"}
        )
    request.state.user_id = "default"
    return True

def get_current_user_id(request: Request) -> str:
    """
    Returns the identity authenticated by the router-level API-key/JWT dependency.
    """
    return getattr(request.state, "user_id", "default")


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256$310000${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_value, digest_value = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_value + "=" * (-len(salt_value) % 4))
        expected = base64.urlsafe_b64decode(digest_value + "=" * (-len(digest_value) % 4))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: str) -> str:
    now = int(time.time())
    payload = {"sub": user_id, "iat": now, "exp": now + settings.ACCESS_TOKEN_TTL_MINUTES * 60}
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = f"{_b64encode(json.dumps(header, separators=(',', ':')).encode())}.{_b64encode(json.dumps(payload, separators=(',', ':')).encode())}"
    signature = hmac.new(settings.AUTH_SECRET.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64encode(signature)}"


def decode_access_token(token: str) -> Optional[str]:
    try:
        header_value, payload_value, signature_value = token.split(".", 2)
        header = json.loads(base64.urlsafe_b64decode(header_value + "=" * (-len(header_value) % 4)))
        payload = json.loads(base64.urlsafe_b64decode(payload_value + "=" * (-len(payload_value) % 4)))
        if header.get("alg") != "HS256":
            return None
        signing_input = f"{header_value}.{payload_value}"
        expected = hmac.new(settings.AUTH_SECRET.encode(), signing_input.encode(), hashlib.sha256).digest()
        signature = base64.urlsafe_b64decode(signature_value + "=" * (-len(signature_value) % 4))
        if not hmac.compare_digest(expected, signature) or int(payload.get("exp", 0)) <= int(time.time()):
            return None
        subject = payload.get("sub")
        return subject if isinstance(subject, str) and subject else None
    except (ValueError, TypeError, json.JSONDecodeError):
        return None
