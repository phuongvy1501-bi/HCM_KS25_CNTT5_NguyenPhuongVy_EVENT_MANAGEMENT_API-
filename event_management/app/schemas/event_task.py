from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.event_task import TaskStatus, TaskPriority


class EventTaskBase(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None


class EventTaskCreate(EventTaskBase):
    pass


class EventTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None


class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    status: TaskStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
