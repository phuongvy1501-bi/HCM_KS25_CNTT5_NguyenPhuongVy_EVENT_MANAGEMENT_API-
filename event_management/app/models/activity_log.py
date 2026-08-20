import enum
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ActivityAction(str, enum.Enum):
    EVENT_CREATED = "EVENT_CREATED"
    EVENT_UPDATED = "EVENT_UPDATED"
    EVENT_DELETED = "EVENT_DELETED"
    MEMBER_ADDED = "MEMBER_ADDED"
    MEMBER_REMOVED = "MEMBER_REMOVED"


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[ActivityAction] = mapped_column(
        Enum(ActivityAction, native_enum=False, length=30), nullable=False
    )
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    event = relationship("Event", foreign_keys=[event_id])
    actor = relationship("User", foreign_keys=[actor_id])

    def __repr__(self) -> str:
        return f"<ActivityLog event_id={self.event_id} action={self.action}>"
