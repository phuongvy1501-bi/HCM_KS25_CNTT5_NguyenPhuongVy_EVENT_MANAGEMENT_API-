from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventMemberAdd,
    EventStaffResponse,
)
from app.dependencies.auth import get_current_user
from app.services import event_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.create_event(db, data, owner_id=current_user.id)


@router.get("", response_model=list[EventResponse])
def list_my_events(
    search: str | None = Query(None, description="Tìm theo tên sự kiện"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.list_my_events(db, user_id=current_user.id, search=search)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.get_event_detail(db, event_id, user_id=current_user.id)


@router.patch("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.update_event(db, event_id, data, user_id=current_user.id)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event_service.delete_event(db, event_id, user_id=current_user.id)



@router.post("/{event_id}/members", response_model=EventStaffResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    event_id: int,
    data: EventMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.add_member(db, event_id, data, actor_id=current_user.id)


@router.get("/{event_id}/members", response_model=list[EventStaffResponse])
def list_members(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ds thành viên sự kiện."""
    return event_service.list_members(db, event_id, user_id=current_user.id)


@router.delete("/{event_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event_service.remove_member(db, event_id, target_user_id=user_id, actor_id=current_user.id)
