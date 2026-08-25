from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

# Engine kết nối tới MySQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # tự kiểm tra kết nối "sống" trước khi dùng, tránh lỗi timeout MySQL
    echo=settings.DEBUG,  # in SQL log khi DEBUG=True, tắt ở production
)

# Factory tạo session làm việc với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class dùng chung cho toàn bộ SQLAlchemy models."""
    pass


def get_db():
    """
    Dependency cấp session DB cho từng request,
    tự động đóng session sau khi request kết thúc.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
