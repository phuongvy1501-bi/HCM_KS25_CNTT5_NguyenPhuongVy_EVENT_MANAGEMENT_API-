import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

from app.db.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.event import Event, EventStaff, EventStaffRole
from app.models.event_task import EventTask, TaskStatus, TaskPriority


def seed():
    db = SessionLocal()
    try:
        # ---- Users ----
        admin = User(
            email="admin@example.com",
            password_hash=hash_password("Admin@123"),
            full_name="Quản trị viên",
            role=UserRole.ADMIN,
        )
        owner = User(
            email="owner@example.com",
            password_hash=hash_password("Owner@123"),
            full_name="Nguyễn Văn Owner",
            role=UserRole.USER,
        )
        member = User(
            email="member@example.com",
            password_hash=hash_password("Member@123"),
            full_name="Trần Thị Member",
            role=UserRole.USER,
        )
        db.add_all([admin, owner, member])
        db.commit()
        db.refresh(owner)
        db.refresh(member)

        # ---- Event ----
        event = Event(
            name="Hội thảo FastAPI 2026",
            description="Sự kiện demo dự án Event Management API",
            owner_id=owner.id,
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        # ---- EventStaff ----
        db.add_all([
            EventStaff(event_id=event.id, user_id=owner.id, role=EventStaffRole.OWNER),
            EventStaff(event_id=event.id, user_id=member.id, role=EventStaffRole.MEMBER),
        ])
        db.commit()

        # ---- EventTask ----
        db.add_all([
            EventTask(
                event_id=event.id,
                title="Chuẩn bị slide trình bày",
                description="Soạn slide giới thiệu dự án",
                assignee_id=member.id,
                status=TaskStatus.TODO,
                priority=TaskPriority.HIGH,
                due_date=datetime.utcnow() + timedelta(days=3),
            ),
            EventTask(
                event_id=event.id,
                title="Đặt phòng hội thảo",
                description="Liên hệ đặt phòng cho sự kiện",
                assignee_id=owner.id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.MEDIUM,
                due_date=datetime.utcnow() + timedelta(days=1),
            ),
        ])
        db.commit()

        print("Seed dữ liệu thành công!")
    except Exception as e:
        db.rollback()
        print(f"Seed thất bại: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
