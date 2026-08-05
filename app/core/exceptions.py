import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """도메인에서 의도적으로 발생시키는 예상 가능한 오류의 공통 베이스.

    구체적인 비즈니스 규칙(어떤 리소스가 언제 못 찾아지는지 등)은 이 클래스가
    알지 못한다. 각 도메인은 이 클래스를 상속해 code/message/status_code를
    채워 사용한다.
    """

    code: str = "APP_ERROR"
    message: str = "요청을 처리할 수 없습니다."
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: Any | None = None,
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppError):
    """여러 도메인이 공통으로 쓰는 범용 404. 도메인별 세부 사유는 message/details로 전달한다."""

    code = "RESOURCE_NOT_FOUND"
    message = "요청한 리소스를 찾을 수 없습니다."
    status_code = status.HTTP_404_NOT_FOUND


def _error_response(code: str, message: str, details: Any | None, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "details": details},
    )


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # Starlette add_exception_handler는 핸들러 시그니처를 Callable[[Request, Exception], ...]로
    # 요구한다. 실제로는 등록한 예외 타입으로만 호출되므로 안전하게 narrowing한다.
    assert isinstance(exc, AppError)
    return _error_response(exc.code, exc.message, exc.details, exc.status_code)


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    return _error_response(
        code="VALIDATION_ERROR",
        message="요청 값이 올바르지 않습니다.",
        details=exc.errors(),
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # 클라이언트에는 traceback을 노출하지 않고 서버 로그에만 남긴다.
    logger.exception("Unhandled exception while processing request", exc_info=exc)
    return _error_response(
        code="INTERNAL_SERVER_ERROR",
        message="서버에서 예상하지 못한 오류가 발생했습니다.",
        details=None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    # Exception 핸들러를 등록해 두면 DEBUG 여부와 무관하게 Starlette가
    # 기본 HTML traceback 대신 이 핸들러를 사용한다.
    app.add_exception_handler(Exception, unhandled_exception_handler)
