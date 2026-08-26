from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
)
from app.routers import auth, users, event as event_router, event_task
from app.db.database import engine
from app.models import user, event as event_model

# 1. Khởi tạo app trước tiên
app = FastAPI(
    title=settings.APP_NAME,
    description="",
    version="1.0.0",
    debug=settings.DEBUG,
)

# 2. Sự kiện startup gắn vào app
@app.on_event("startup")
def startup_event():
    user.Base.metadata.create_all(bind=engine)

# ===== Middleware =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(event_router.router)
app.include_router(event_task.event_tasks_under_event_router)
app.include_router(event_task.event_tasks_router)


@app.get(
    "/health",
    tags=["Health"],
    summary="Kiểm tra tình trạng server",
    description="Endpoint đơn giản để kiểm tra server còn hoạt động.",
)
def health_check():
    return {
        "success": True,
        "status": "ok",
        "app_name": settings.APP_NAME,
    }