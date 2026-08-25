from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.core.exceptions import UnauthorizedException, ForbiddenException

# tokenUrl chỉ dùng để hiển thị nút "Authorize" trên Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency trung tâm: giải mã JWT từ header Authorization: Bearer <token>,
    load user tương ứng từ DB, dùng cho mọi endpoint cần đăng nhập.
    """
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedException("Token không hợp lệ hoặc đã hết hạn")

    if payload.get("type") != "access":
        raise UnauthorizedException("Token không phải access token")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Token thiếu thông tin người dùng")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise UnauthorizedException("Người dùng không tồn tại")

    if not user.is_active:
        raise UnauthorizedException("Tài khoản đã bị vô hiệu hóa")

    return user


def require_roles(*allowed_roles: UserRole):
    """
    Factory tạo dependency kiểm tra role.
    Dùng: Depends(require_roles(UserRole.ADMIN))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException("Bạn không có quyền thực hiện thao tác này")
        return current_user

    return role_checker
