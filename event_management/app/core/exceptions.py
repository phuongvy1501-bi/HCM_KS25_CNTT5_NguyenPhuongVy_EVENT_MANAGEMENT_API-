from datetime import datetime, timezone

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base exception cho toàn bộ lỗi nghiệp vụ trong app."""

    def __init__(self, status_code: int, message: str, error_code: str | None = None):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code or "ERROR"


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, message, error_code="NOT_FOUND")


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, error_code="BAD_REQUEST")


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(status.HTTP_403_FORBIDDEN, message, error_code="FORBIDDEN")


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, error_code="UNAUTHORIZED")


def build_error_response(status_code: int, message: str, error_code: str, path: str) -> dict:
    """
    Format thống nhất cho MỌI lỗi trả về, gồm đúng 6 trường:
    success, code, message, data, error, timestamp (path đính kèm để debug).
    """
    return {
        "success": False,
        "code": status_code,
        "message": message,
        "data": None,
        "error": error_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": path,
    }


async def app_exception_handler(request: Request, exc: AppException):
    """Format lỗi thống nhất cho toàn bộ response lỗi nghiệp vụ trong hệ thống."""
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            path=str(request.url.path),
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Bắt các lỗi không lường trước (500), tránh lộ stacktrace ra ngoài."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_error_response(
            status_code=500,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            path=str(request.url.path),
        ),
    )
