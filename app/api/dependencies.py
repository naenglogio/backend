from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.domains.users.service import InvalidTokenError, decode_access_token

# 도메인 router는 이 타입을 그대로 파라미터에 써서 요청마다 DB 세션을 받는다.
# commit 경계는 이 dependency가 아니라 service/repository가 정한다(04단계 설계 유지).
DBSession = Annotated[AsyncSession, Depends(get_db_session)]

# auto_error=False로 두고 헤더 누락도 직접 InvalidTokenError로 통일한다.
# 기본값(auto_error=True)은 헤더가 없을 때 우리 공통 에러 포맷과 다른
# {"detail": "Not authenticated"}를 반환해서 응답 계약이 어긋난다.
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> int:
    """Authorization 헤더의 JWT에서 현재 사용자 id를 반환하는 공통 계약.

    토큰 검증 자체는 app.domains.users.service.decode_access_token이 하고,
    여기서는 그 결과를 다른 도메인이 재사용할 수 있는 형태로만 노출한다.
    헤더 누락·서명 불일치·만료는 모두 InvalidTokenError(401)로 통일한다.

    테스트에서는 `app.dependency_overrides[get_current_user_id] = lambda: 1`
    처럼 override해서 인증 없이 특정 사용자로 요청을 검증한다.
    """
    if credentials is None:
        raise InvalidTokenError()
    return decode_access_token(credentials.credentials)


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
