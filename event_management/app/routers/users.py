from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse
from app.dependencies.auth import get_current_user, require_roles
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Thông tin cá nhân",
    description="Trả về thông tin của chính người dùng đang đăng nhập. "
                 "Trường password_hash không bao giờ xuất hiện trong response.",
)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Danh sách user (chỉ Admin)",
    description="Chỉ tài khoản có role ADMIN mới gọi được endpoint này. "
                 "Hỗ trợ tìm kiếm theo tên/email và lọc theo trạng thái hoạt động.",
    responses={403: {"description": "Không có quyền ADMIN"}},
)
def list_users(
    search: str | None = Query(None, description="Tìm theo tên hoặc email"),
    is_active: bool | None = Query(None, description="Lọc theo trạng thái hoạt động"),
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua (phân trang)"),
    limit: int = Query(20, ge=1, le=100, description="Số bản ghi tối đa trả về"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return user_service.get_users(db, search=search, is_active=is_active, skip=skip, limit=limit)
