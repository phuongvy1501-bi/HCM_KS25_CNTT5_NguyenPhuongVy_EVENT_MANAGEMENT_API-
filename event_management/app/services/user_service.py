from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User


def get_users(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[User]:
    """Trả về danh sách user, hỗ trợ search theo tên/email và filter trạng thái."""
    query = db.query(User)

    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(User.full_name.ilike(pattern), User.email.ilike(pattern)))

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
