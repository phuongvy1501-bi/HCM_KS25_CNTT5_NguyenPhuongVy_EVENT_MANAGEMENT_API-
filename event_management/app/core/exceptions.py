from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base exception cho toàn bộ lỗi nghiệp vụ trong app."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, message)


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(status.HTTP_400_BAD_REQUEST, message)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(status.HTTP_403_FORBIDDEN, message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message)


async def app_exception_handler(request: Request, exc: AppException):
    """Format lỗi thống nhất cho toàn bộ response lỗi trong hệ thống."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.message,
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Bắt các lỗi không lường trước (500), tránh lộ stacktrace ra ngoài."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
            },
        },
    )
