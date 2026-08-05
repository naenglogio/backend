from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """공통 오류 응답 계약.

    app.core.exceptions의 핸들러가 실제로 만드는 JSON과 형태를 맞춘다.
    OpenAPI 문서에 노출하기 위한 용도이며, 핸들러 자체는 이 모델을 거치지 않고
    같은 모양의 dict를 직접 반환한다(런타임 오버헤드를 늘리지 않기 위함).
    """

    code: str
    message: str
    details: Any | None = None


class PageMeta(BaseModel):
    """목록 응답의 페이지네이션 메타데이터. page는 1부터 시작한다."""

    page: int
    size: int
    total: int


class Page[T](BaseModel):
    """MVP 목록 응답 표준 형태: page/size/total/items.

    사용 예: `Page[UserRead]`처럼 도메인 read schema를 타입 인자로 넣는다.
    """

    items: list[T]
    page: int
    size: int
    total: int


# 도메인 route에 공통으로 붙일 오류 응답 문서 조각. 예:
#   api_router.include_router(users_router, responses=COMMON_ERROR_RESPONSES)
COMMON_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    422: {"model": ErrorResponse, "description": "요청 값 검증 실패"},
    500: {"model": ErrorResponse, "description": "예상하지 못한 서버 오류"},
}
