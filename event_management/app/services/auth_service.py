from sqlalchemy.orm import Session
from jose import JWTError

from app.models.user import User, UserRole
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.schemas.auth import RegisterRequest, LoginRequest


def register_user(db: Session, data: RegisterRequest) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise BadRequestException("Email đã được sử dụng")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: LoginRequest) -> User:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        # Không tiết lộ email hay password sai để tránh dò email tồn tại
        raise UnauthorizedException("Email hoặc mật khẩu không đúng")

    if not user.is_active:
        raise UnauthorizedException("Tài khoản đã bị vô hiệu hóa")

    return user


def issue_token_pair(user: User) -> tuple[str, str]:
    access_token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
    refresh_token = create_refresh_token(subject=str(user.id))
    return access_token, refresh_token


def refresh_access_token(db: Session, refresh_token: str) -> str:
    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise UnauthorizedException("Refresh token không hợp lệ hoặc đã hết hạn")

    if payload.get("type") != "refresh":
        raise UnauthorizedException("Token không phải loại refresh token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise UnauthorizedException("Người dùng không tồn tại")
    if not user.is_active:
        raise UnauthorizedException("Tài khoản đã bị vô hiệu hóa")

    return create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
