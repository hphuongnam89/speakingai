from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, hash_password, verify_password, verify_api_key, get_current_principal_id
from app.core.config import settings
from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.auth import AuthRequest, AuthResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def check_browser_origin(request: Request):
    if request.headers.get("X-Browser-Session") == "true" and request.headers.get("origin") != str(request.base_url).rstrip("/"):
        raise HTTPException(status_code=403, detail="Same-origin request required")


def browser_session(request: Request, response: Response, token: str):
    if request.headers.get("X-Browser-Session") == "true":
        if request.headers.get("origin") != str(request.base_url).rstrip("/"):
            raise HTTPException(status_code=403, detail="Same-origin request required")
        response.set_cookie("learning_session", token, httponly=True, samesite="strict",
                            secure=request.url.scheme == "https", path="/",
                            max_age=settings.ACCESS_TOKEN_TTL_MINUTES * 60)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: AuthRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    check_browser_origin(request)
    email = payload.email.strip().lower()
    if db.query(UserModel).filter(UserModel.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = UserModel(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    db.refresh(user)
    token = create_access_token(user.id)
    browser_session(request, response, token)
    return AuthResponse(access_token=token, expires_in=settings.ACCESS_TOKEN_TTL_MINUTES * 60, user_id=user.id)


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    check_browser_origin(request)
    email = payload.email.strip().lower()
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    browser_session(request, response, token)
    return AuthResponse(access_token=token, expires_in=settings.ACCESS_TOKEN_TTL_MINUTES * 60, user_id=user.id)


@router.get("/session", dependencies=[Depends(verify_api_key)])
def session_status(request: Request):
    principal = get_current_principal_id(request)
    if principal == "default":
        raise HTTPException(status_code=401, detail="Please sign in")
    return {"user_id": principal}


@router.post("/logout")
def logout(request: Request, response: Response):
    if request.headers.get("origin") != str(request.base_url).rstrip("/"):
        raise HTTPException(status_code=403, detail="Same-origin request required")
    response.delete_cookie("learning_session", path="/", httponly=True, samesite="strict")
    return {"status": "signed_out"}
