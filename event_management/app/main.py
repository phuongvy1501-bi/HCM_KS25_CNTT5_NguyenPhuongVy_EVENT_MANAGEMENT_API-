from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
)
from app.routers import auth, users, event, event_task

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API quản lý sự kiện: đăng ký/đăng nhập (JWT), quản lý sự kiện, "
        "thành viên sự kiện và công việc sự kiện (event tasks) với phân "
        "quyền theo vai trò Owner/Member/Assignee."
    ),
    version="1.0.0",
    debug=settings.DEBUG,
)

# ===== Middleware =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # mở toàn bộ khi dev, sẽ siết lại ở production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Exception handlers =====
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ===== Routers =====
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(event.router)
app.include_router(event_task.event_tasks_under_event_router)
app.include_router(event_task.event_tasks_router)


@app.get(
    "/health",
    tags=["Health"],
    summary="Kiểm tra tình trạng server",
    description="Endpoint đơn giản để kiểm tra server còn hoạt động, dùng cho "
                 "monitoring hoặc demo nhanh.",
)
def health_check():
    return {
        "success": True,
        "status": "ok",
        "app_name": settings.APP_NAME,
    }
