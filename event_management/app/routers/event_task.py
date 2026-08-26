from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.event_task import TaskStatus, TaskPriority
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate, EventTaskResponse
from app.dependencies.auth import get_current_user
from app.services import event_task_service

# Router 1: các endpoint nằm dưới /events/{event_id}/event-tasks
event_tasks_under_event_router = APIRouter(prefix="/events", tags=["Event Tasks"])

# Router 2: endpoint thao tác trực tiếp trên 1 task theo id, không cần biết event_id trước
event_tasks_router = APIRouter(prefix="/event-tasks", tags=["Event Tasks"])


@event_tasks_under_event_router.post(
    "/{event_id}/event-tasks",
    response_model=EventTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo công việc sự kiện",
    description="Bất kỳ thành viên (Owner hoặc Member) nào của sự kiện đều có quyền "
                 "tạo công việc mới. Nếu chỉ định assignee_id, người được giao việc "
                 "bắt buộc phải là thành viên đã tham gia sự kiện này.",
    responses={403: {"description": "Không phải thành viên sự kiện"}, 404: {"description": "Sự kiện không tồn tại"}},
)
def create_event_task(
    event_id: int,
    data: EventTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_task_service.create_task(db, event_id, data, actor_id=current_user.id)


@event_tasks_under_event_router.get(
    "/{event_id}/event-tasks",
    response_model=list[EventTaskResponse],
    summary="Danh sách công việc của sự kiện",
    description="Trả về công việc thuộc đúng sự kiện này, không lộ công việc của sự "
                 "kiện khác. Hỗ trợ filter theo status/priority/assignee, search theo "
                 "tiêu đề, phân trang bằng skb cip/limit, sắp xếp theo created_at hoặc due_date.",
)
def list_event_tasks(
    event_id: int,
    status_filter: TaskStatus | None = Query(None, alias="status", description="Lọc theo trạng thái"),
    priority: TaskPriority | None = Query(None, description="Lọc theo độ ưu tiên"),
    assignee_id: int | None = Query(None, description="Lọc theo người được giao việc"),
    search: str | None = Query(None, description="Tìm theo tiêu đề công việc"),
    sort_by: str = Query("created_at", pattern="^(created_at|due_date)$", description="Sắp xếp theo created_at hoặc due_date"),
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua (phân trang)"),
    limit: int = Query(20, ge=1, le=100, description="Số bản ghi tối đa trả về"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_task_service.list_tasks(
        db,
        event_id,
        user_id=current_user.id,
        status_filter=status_filter,
        priority_filter=priority,
        assignee_id=assignee_id,
        search=search,
        sort_by=sort_by,
        skip=skip,
        limit=limit,
    )


@event_tasks_router.get(
    "/{task_id}",
    response_model=EventTaskResponse,
    summary="Chi tiết công việc sự kiện",
    description="Kiểm tra user hiện tại có thuộc sự kiện chứa công việc này không, "
                 "trước khi trả dữ liệu chi tiết.",
    responses={403: {"description": "Không phải thành viên sự kiện"}, 404: {"description": "Công việc không tồn tại"}},
)
def get_event_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_task_service.get_task_detail(db, task_id, user_id=current_user.id)


@event_tasks_router.patch(
    "/{task_id}",
    response_model=EventTaskResponse,
    summary="Cập nhật công việc sự kiện",
    description="Chỉ Owner của sự kiện hoặc chính Assignee của công việc mới được cập "
                 "nhật. Chỉ field nào thực sự được gửi lên trong body mới bị ghi đè, "
                 "các field không gửi lên giữ nguyên giá trị cũ.",
    responses={403: {"description": "Không có quyền cập nhật công việc này"}, 404: {"description": "Công việc không tồn tại"}},
)
def update_event_task(
    task_id: int,
    data: EventTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_task_service.update_task(db, task_id, data, user_id=current_user.id)


@event_tasks_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xoá công việc sự kiện",
    description="Chỉ Owner của sự kiện hoặc chính Assignee của công việc mới được xoá.",
    responses={403: {"description": "Không có quyền xoá công việc này"}, 404: {"description": "Công việc không tồn tại"}},
)
def delete_event_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event_task_service.delete_task(db, task_id, user_id=current_user.id)
