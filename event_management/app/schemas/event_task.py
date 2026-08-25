from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

from app.models.event_task import TaskStatus, TaskPriority


class EventTaskBase(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Tiêu đề công việc không được để trống")
        if len(v) > 255:
            raise ValueError("Tiêu đề tối đa 255 ký tự")
        return v.strip()


class EventTaskCreate(EventTaskBase):
    pass


class EventTaskUpdate(BaseModel):
    """
    Tất cả field đều optional — field nào không gửi lên (giữ None)
    sẽ KHÔNG bị ghi đè trong DB, chỉ field nào có giá trị mới được cập nhật.
    """
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Tiêu đề công việc không được để trống")
        return v.strip() if v else v


class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    status: TaskStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
