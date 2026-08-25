from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

from app.models.event import EventStaffRole
from app.schemas.user import UserResponse


class EventBase(BaseModel):
    name: str
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Tên sự kiện không được để trống")
        if len(v) > 255:
            raise ValueError("Tên sự kiện tối đa 255 ký tự")
        return v.strip()


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventMemberAdd(BaseModel):
    user_id: int
    role: EventStaffRole = EventStaffRole.MEMBER


class EventStaffResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    role: EventStaffRole
    joined_at: datetime
    user: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)
