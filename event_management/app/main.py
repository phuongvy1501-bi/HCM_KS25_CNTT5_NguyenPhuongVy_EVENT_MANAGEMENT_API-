from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
)
from app.routers import auth, users, event

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # mở toàn bộ khi dev, sẽ siết lại ở production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(event.router)


@app.get("/health", tags=["Health"])
def health_check():
    """Kiểm tra ứng dụng còn sống, dùng cho monitoring/demo."""
    return {
        "success": True,
        "status": "ok",
        "app_name": settings.APP_NAME,
    }
