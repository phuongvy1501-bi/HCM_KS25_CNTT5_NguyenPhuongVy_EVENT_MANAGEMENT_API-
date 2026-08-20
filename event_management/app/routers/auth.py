from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.user import UserResponse
from app.schemas.token import TokenResponse, AccessTokenResponse, RefreshTokenRequest
from app.services import auth_service
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """dky tài khoản mới"""
    user = auth_service.register_user(db, data)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    """Đăng nhập, trả về access_token + refresh_token."""
    user = auth_service.authenticate_user(db, data)
    access_token, refresh_token = auth_service.issue_token_pair(user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Cấp lại access token mới từ refresh token còn hiệu lực."""
    new_access_token = auth_service.refresh_access_token(db, data.refresh_token)
    return AccessTokenResponse(access_token=new_access_token)
