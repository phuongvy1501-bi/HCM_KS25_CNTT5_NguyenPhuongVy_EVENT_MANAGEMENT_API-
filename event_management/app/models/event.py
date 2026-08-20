import enum
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base


class EventStaffRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relationships
    owner = relationship("User", back_populates="owned_events", foreign_keys=[owner_id])
    staff = relationship(
        "EventStaff", back_populates="event", cascade="all, delete-orphan"
    )
    tasks = relationship(
        "EventTask", back_populates="event", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Event id={self.id} name={self.name}>"


class EventStaff(Base):
    __tablename__ = "event_staff"
    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_event_staff_event_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[EventStaffRole] = mapped_column(
        Enum(EventStaffRole, native_enum=False, length=20), nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relationships
    event = relationship("Event", back_populates="staff", foreign_keys=[event_id])
    user = relationship("User", back_populates="event_memberships", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<EventStaff event_id={self.event_id} user_id={self.user_id} role={self.role}>"
