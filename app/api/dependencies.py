from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.db.session import get_db_session

# 도메인 router는 이 타입을 그대로 파라미터에 써서 요청마다 DB 세션을 받는다.
# commit 경계는 이 dependency가 아니라 service/repository가 정한다(04단계 설계 유지).
DBSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user_id() -> int:
    """현재 사용자 id를 반환하는 교체 가능한 계약.

    인증이 아직 구현되지 않았으므로 항상 501로 명확히 실패한다. 실제 인증이
    만들어지면 이 함수의 본문만 토큰 검증 로직으로 교체하면 되고, 다른 코드는
    `CurrentUserId` 타입을 그대로 쓰면 된다.

    테스트에서는 `app.dependency_overrides[get_current_user_id] = lambda: 1`
    처럼 override해서 인증 없이 특정 사용자로 요청을 검증한다.
    """
    raise AppError(
        code="AUTH_NOT_IMPLEMENTED",
        message="인증이 아직 구현되지 않았습니다.",
        status_code=501,
    )


CurrentUserId = Annotated[int, Depends(get_current_user_id)]


class PageParams:
    """목록 조회 공통 query parameter. page는 1부터 시작한다."""

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="1부터 시작하는 페이지 번호"),
        size: int = Query(default=20, ge=1, le=100, description="페이지당 항목 수"),
    ) -> None:
        self.page = page
        self.size = size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


PageQuery = Annotated[PageParams, Depends(PageParams)]
