from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str  # plain password nhận từ client, sẽ hash trước khi lưu DB


class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListQuery(BaseModel):
    search: str | None = None      # tìm theo tên hoặc email
    is_active: bool | None = None  # lọc theo trạng thái
