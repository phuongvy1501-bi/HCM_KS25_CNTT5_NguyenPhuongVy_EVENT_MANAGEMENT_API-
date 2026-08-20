from sqlalchemy.orm import Session

from app.models.event import Event, EventStaff, EventStaffRole
from app.models.activity_log import ActivityAction
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.schemas.event import EventCreate, EventUpdate, EventMemberAdd
from app.services.activity_log_service import log_activity



def get_membership(db: Session, event_id: int, user_id: int) -> EventStaff | None:
    return (db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id).first())


def get_active_event_or_404(db: Session, event_id: int) -> Event:
    event = db.query(Event).filter(Event.id == event_id, Event.is_deleted == False).first()  # noqa: E712
    if not event:
        raise NotFoundException("Sự kiện không tồn tại")
    return event


def ensure_is_member(db: Session, event_id: int, user_id: int) -> EventStaff:
    membership = get_membership(db, event_id, user_id)
    if not membership:
        raise ForbiddenException("Bạn không phải thành viên của sự kiện này")
    return membership


def ensure_is_owner(db: Session, event_id: int, user_id: int) -> EventStaff:
    membership = ensure_is_member(db, event_id, user_id)
    if membership.role != EventStaffRole.OWNER:
        raise ForbiddenException("Chỉ Owner mới có quyền thực hiện thao tác này")
    return membership



def create_event(db: Session, data: EventCreate, owner_id: int) -> Event:
    event = Event(name=data.name, description=data.description, owner_id=owner_id)
    db.add(event)
    db.commit()
    db.refresh(event)

    # Owner tự động là thành viên với role OWNER
    staff = EventStaff(event_id=event.id, user_id=owner_id, role=EventStaffRole.OWNER)
    db.add(staff)
    db.commit()

    log_activity(db, event.id, owner_id, ActivityAction.EVENT_CREATED, detail=f"Tạo sự kiện '{event.name}'")
    return event


def list_my_events(db: Session, user_id: int, search: str | None = None) -> list[Event]:
    query = (db.query(Event).join(EventStaff, EventStaff.event_id == Event.id).filter(EventStaff.user_id == user_id, Event.is_deleted == False))
    if search:
        query = query.filter(Event.name.ilike(f"%{search}%"))
    return query.order_by(Event.created_at.desc()).all()


def get_event_detail(db: Session, event_id: int, user_id: int) -> Event:
    event = get_active_event_or_404(db, event_id)
    ensure_is_member(db, event_id, user_id)  # chỉ thành viên mới được xem
    return event


def update_event(db: Session, event_id: int, data: EventUpdate, user_id: int) -> Event:
    event = get_active_event_or_404(db, event_id)
    ensure_is_owner(db, event_id, user_id)  # chỉ Owner mới được sửa

    if data.name is not None:
        event.name = data.name
    if data.description is not None:
        event.description = data.description

    db.commit()
    db.refresh(event)
    log_activity(db, event.id, user_id, ActivityAction.EVENT_UPDATED, detail=f"Cập nhật sự kiện '{event.name}'")
    return event


def delete_event(db: Session, event_id: int, user_id: int) -> None:
    """Soft delete: chỉ đánh dấu is_deleted, không xoá vật lý."""
    event = get_active_event_or_404(db, event_id)
    ensure_is_owner(db, event_id, user_id)  # chỉ Owner mới được xoá

    event.is_deleted = True
    db.commit()
    log_activity(db, event.id, user_id, ActivityAction.EVENT_DELETED, detail=f"Xoá sự kiện '{event.name}'")



def add_member(db: Session, event_id: int, data: EventMemberAdd, actor_id: int) -> EventStaff:
    get_active_event_or_404(db, event_id)
    ensure_is_owner(db, event_id, actor_id)  # chỉ Owner được thêm

    existing = get_membership(db, event_id, data.user_id)
    if existing:
        raise BadRequestException("Người dùng đã là thành viên của sự kiện")

    staff = EventStaff(event_id=event_id, user_id=data.user_id, role=data.role)
    db.add(staff)
    db.commit()
    db.refresh(staff)

    log_activity(db, event_id, actor_id, ActivityAction.MEMBER_ADDED, detail=f"Thêm user_id={data.user_id}")
    return staff


def list_members(db: Session, event_id: int, user_id: int) -> list[EventStaff]:
    get_active_event_or_404(db, event_id)
    ensure_is_member(db, event_id, user_id)  # thành viên nào cũng xem được danh sách
    return db.query(EventStaff).filter(EventStaff.event_id == event_id).all()


def remove_member(db: Session, event_id: int, target_user_id: int, actor_id: int) -> None:
    get_active_event_or_404(db, event_id)
    ensure_is_owner(db, event_id, actor_id)  # chỉ Owner được xoá thành viên

    target = get_membership(db, event_id, target_user_id)
    if not target:
        raise NotFoundException("Thành viên không tồn tại trong sự kiện")

    if target.role == EventStaffRole.OWNER:
        owner_count = (
            db.query(EventStaff)
            .filter(EventStaff.event_id == event_id, EventStaff.role == EventStaffRole.OWNER)
            .count()
        )
        if owner_count <= 1:
            raise BadRequestException("Không thể xoá Owner cuối cùng của sự kiện")

    db.delete(target)
    db.commit()
    log_activity(db, event_id, actor_id, ActivityAction.MEMBER_REMOVED, detail=f"Xoá user_id={target_user_id}")
