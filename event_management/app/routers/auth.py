from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserResponse
from app.schemas.token import TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    description="Tạo tài khoản mới với role mặc định USER. Email phải chưa tồn tại, "
                 "password tối thiểu 6 ký tự. Mật khẩu được hash bằng bcrypt trước khi lưu.",
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, data)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Đăng nhập, nhận access token",
    description="Sử dụng chuẩn OAuth2 Password Flow — gửi dữ liệu dạng "
                 "x-www-form-urlencoded với 2 field `username` (chính là email) và "
                 "`password`. Đây là format bắt buộc để nút Authorize trên Swagger UI "
                 "hoạt động đúng.",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm luôn đặt tên field là "username",
    user = auth_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    access_token = auth_service.issue_access_token(user)
    return TokenResponse(access_token=access_token)
