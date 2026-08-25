from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog, ActivityAction


def log_activity(db: Session, event_id: int, actor_id: int, action: ActivityAction, detail: str | None = None):
    """Ghi lại lịch sử thao tác quan trọng lên sự kiện."""
    entry = ActivityLog(event_id=event_id, actor_id=actor_id, action=action, detail=detail)
    db.add(entry)
    db.commit()
