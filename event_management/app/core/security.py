from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Cấu hình bcrypt để hash password, tuyệt đối không lưu plain text
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash mật khẩu thô thành chuỗi bcrypt để lưu vào DB."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So khớp mật khẩu người dùng nhập với hash đã lưu trong DB."""
    return pwd_context.verify(plain_password, hashed_password)


# ============ JWT ============

def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """
    Tạo access token dùng cho mọi request cần xác thực.
    subject = user id (dạng string), sẽ được lưu vào field "sub".
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire, "type": "access"}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Giải mã token, raise jose.JWTError nếu token sai chữ ký hoặc hết hạn.
    Việc bắt lỗi và convert sang HTTPException sẽ do dependency đảm nhiệm.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
