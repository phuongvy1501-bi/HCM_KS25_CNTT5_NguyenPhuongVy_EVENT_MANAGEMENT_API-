from sqlalchemy.orm import Session

from app.models.event import Event, EventStaff, EventStaffRole
from app.models.event_task import EventTask, TaskStatus, TaskPriority
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.schemas.event_task import EventTaskCreate, EventTaskUpdate
from app.services.event_service import get_event_or_404, get_membership, ensure_is_member


# ---------- Helpers ----------

def get_task_or_404(db: Session, task_id: int) -> EventTask:
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if not task:
        raise NotFoundException("Công việc sự kiện không tồn tại")
    return task


def ensure_assignee_is_event_staff(db: Session, event_id: int, assignee_id: int) -> None:
    """
    'Giao việc': assignee bắt buộc phải là thành viên (staff) đã tham gia sự kiện,
    KHÔNG được gán việc cho người ngoài sự kiện.
    """
    membership = get_membership(db, event_id, assignee_id)
    if not membership:
        raise BadRequestException("Chỉ có thể giao việc cho thành viên đã tham gia sự kiện")


def can_manage_task(db: Session, event_id: int, task: EventTask, user_id: int) -> bool:
    """
    Permission matrix cho việc SỬA/XOÁ 1 task cụ thể:
    - Owner của sự kiện: toàn quyền trên mọi task.
    - Assignee của chính task đó: được sửa task của mình (VD: cập nhật status).
    - Member khác (không phải owner, không phải assignee): KHÔNG được sửa/xoá.
    """
    membership = get_membership(db, event_id, user_id)
    if not membership:
        return False
    if membership.role == EventStaffRole.OWNER:
        return True
    if task.assignee_id == user_id:
        return True
    return False


# ---------- CRUD ----------

def create_task(db: Session, event_id: int, data: EventTaskCreate, actor_id: int) -> EventTask:
    """Bất kỳ thành viên nào của sự kiện cũng có quyền tạo công việc sự kiện."""
    get_event_or_404(db, event_id)
    ensure_is_member(db, event_id, actor_id)  # phải là member mới được tạo

    if data.assignee_id is not None:
        ensure_assignee_is_event_staff(db, event_id, data.assignee_id)

    task = EventTask(
        event_id=event_id,
        title=data.title,
        description=data.description,
        assignee_id=data.assignee_id,
        priority=data.priority,
        due_date=data.due_date,
        status=TaskStatus.TODO,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session,
    event_id: int,
    user_id: int,
    status_filter: TaskStatus | None = None,
    priority_filter: TaskPriority | None = None,
    assignee_id: int | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    skip: int = 0,
    limit: int = 20,
) -> list[EventTask]:
    """
    Danh sách công việc CHỈ trong phạm vi 1 sự kiện — không lộ task của sự kiện khác.
    Hỗ trợ filter theo status/priority/assignee, search theo title, phân trang, sắp xếp.
    """
    get_event_or_404(db, event_id)
    ensure_is_member(db, event_id, user_id)  # chỉ member mới xem được danh sách

    query = db.query(EventTask).filter(EventTask.event_id == event_id)

    if status_filter is not None:
        query = query.filter(EventTask.status == status_filter)
    if priority_filter is not None:
        query = query.filter(EventTask.priority == priority_filter)
    if assignee_id is not None:
        query = query.filter(EventTask.assignee_id == assignee_id)
    if search:
        query = query.filter(EventTask.title.ilike(f"%{search}%"))

    sort_column = EventTask.due_date if sort_by == "due_date" else EventTask.created_at
    query = query.order_by(sort_column.desc())

    return query.offset(skip).limit(limit).all()


def get_task_detail(db: Session, task_id: int, user_id: int) -> EventTask:
    """Chi tiết công việc — bắt buộc kiểm tra user thuộc sự kiện trước khi trả dữ liệu."""
    task = get_task_or_404(db, task_id)
    ensure_is_member(db, task.event_id, user_id)  # chặn user không thuộc sự kiện
    return task


def update_task(db: Session, task_id: int, data: EventTaskUpdate, user_id: int) -> EventTask:
    """
    Cập nhật công việc — chỉ Owner hoặc chính Assignee của task mới được sửa.
    Chỉ field nào client thực sự gửi lên (khác None) mới bị ghi đè.
    """
    task = get_task_or_404(db, task_id)

    if not can_manage_task(db, task.event_id, task, user_id):
        raise ForbiddenException("Bạn không có quyền cập nhật công việc này")

    update_data = data.model_dump(exclude_unset=True)  # chỉ lấy field client thực sự gửi

    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        ensure_assignee_is_event_staff(db, task.event_id, update_data["assignee_id"])

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, user_id: int) -> None:
    """Xoá công việc — áp dụng permission matrix, chỉ Owner hoặc Assignee được xoá."""
    task = get_task_or_404(db, task_id)

    if not can_manage_task(db, task.event_id, task, user_id):
        raise ForbiddenException("Bạn không có quyền xoá công việc này")

    db.delete(task)
    db.commit()
