"""
Script khởi tạo bảng ban đầu cho database.
Chạy: python scripts/create_tables.py
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import Base, engine
import app.models  # noqa: F401  -> import để đăng ký toàn bộ model vào Base.metadata


def init_db():
    print("Đang tạo bảng trong database...")
    Base.metadata.create_all(bind=engine)
    print("Tạo bảng thành công! Các bảng đã tạo:")
    for table in Base.metadata.tables:
        print(f"  - {table}")


if __name__ == "__main__":
    init_db()
