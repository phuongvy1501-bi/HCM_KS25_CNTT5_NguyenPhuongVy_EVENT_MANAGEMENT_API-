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


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo sự kiện mới",
    description="Người gọi API tự động trở thành Owner của sự kiện vừa tạo.",
)
def create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.create_event(db, data, owner_id=current_user.id)


@router.get(
    "",
    response_model=list[EventResponse],
    summary="Danh sách sự kiện của tôi",
    description="Trả về các sự kiện mà người dùng hiện tại là Owner hoặc Member. "
                 "Hỗ trợ tìm kiếm theo tên sự kiện.",
)
def list_my_events(
    search: str | None = Query(None, description="Tìm theo tên sự kiện"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.list_my_events(db, user_id=current_user.id, search=search)


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Chi tiết sự kiện",
    description="Chỉ thành viên (Owner hoặc Member) của sự kiện mới xem được chi tiết.",
    responses={403: {"description": "Không phải thành viên sự kiện"}, 404: {"description": "Sự kiện không tồn tại"}},
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.get_event_detail(db, event_id, user_id=current_user.id)


@router.patch(
    "/{event_id}",
    response_model=EventResponse,
    summary="Cập nhật sự kiện",
    description="Chỉ Owner của sự kiện mới được cập nhật tên/mô tả.",
    responses={403: {"description": "Chỉ Owner mới có quyền"}, 404: {"description": "Sự kiện không tồn tại"}},
)
def update_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.update_event(db, event_id, data, user_id=current_user.id)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xoá sự kiện",
    description="Chỉ Owner của sự kiện mới được xoá. Đây là xoá vĩnh viễn (hard delete).",
    responses={403: {"description": "Chỉ Owner mới có quyền"}, 404: {"description": "Sự kiện không tồn tại"}},
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event_service.delete_event(db, event_id, user_id=current_user.id)


# ---------- Member endpoints ----------

@router.post(
    "/{event_id}/members",
    response_model=EventStaffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên vào sự kiện",
    description="Chỉ Owner mới được thêm thành viên. user_id phải là tài khoản đã "
                 "tồn tại và chưa là thành viên của sự kiện này.",
    responses={
        400: {"description": "User đã là thành viên"},
        403: {"description": "Chỉ Owner mới có quyền"},
        404: {"description": "Sự kiện hoặc user không tồn tại"},
    },
)
def add_member(
    event_id: int,
    data: EventMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.add_member(db, event_id, data, actor_id=current_user.id)


@router.get(
    "/{event_id}/members",
    response_model=list[EventStaffResponse],
    summary="Danh sách thành viên sự kiện",
    description="Trả về danh sách thành viên kèm role (OWNER/MEMBER) trong sự kiện.",
    responses={403: {"description": "Không phải thành viên sự kiện"}, 404: {"description": "Sự kiện không tồn tại"}},
)
def list_members(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.list_members(db, event_id, user_id=current_user.id)


@router.delete(
    "/{event_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xoá thành viên khỏi sự kiện",
    description="Chỉ Owner mới được xoá. Không thể xoá Owner cuối cùng của sự kiện.",
    responses={
        400: {"description": "Không thể xoá Owner cuối cùng"},
        403: {"description": "Chỉ Owner mới có quyền"},
        404: {"description": "Sự kiện hoặc thành viên không tồn tại"},
    },
)
def remove_member(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event_service.remove_member(db, event_id, target_user_id=user_id, actor_id=current_user.id)
