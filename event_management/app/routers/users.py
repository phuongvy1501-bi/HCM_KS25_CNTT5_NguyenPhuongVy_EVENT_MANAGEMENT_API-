from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse
from app.dependencies.auth import get_current_user, require_roles
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=list[UserResponse])
def list_users(
    search: str | None = Query(None, description="Tìm theo tên hoặc email"),
    is_active: bool | None = Query(None, description="Lọc theo trạng thái hoạt động"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    # Chỉ ADMIN mới được liệt kê toàn bộ user
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return user_service.get_users(db, search=search, is_active=is_active, skip=skip, limit=limit)
