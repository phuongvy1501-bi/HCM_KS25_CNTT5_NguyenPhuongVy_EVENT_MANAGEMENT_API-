from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.schemas.auth import RegisterRequest


def register_user(db: Session, data: RegisterRequest) -> User:
    """Đăng ký tài khoản mới, kiểm tra email trùng trước khi tạo."""
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


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Xác thực email + password. Nhận 2 tham số thô (không phải object Pydantic)
    vì OAuth2PasswordRequestForm trả về form_data.username / form_data.password
    dưới dạng string, không phải JSON body.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        # Không tiết lộ email hay password sai để tránh dò email tồn tại
        raise UnauthorizedException("Email hoặc mật khẩu không đúng")

    if not user.is_active:
        raise UnauthorizedException("Tài khoản đã bị vô hiệu hóa")

    return user


def issue_access_token(user: User) -> str:
    """Sinh access token cho user đã xác thực thành công."""
    return create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
