"""도메인 Router 조립 지점.

여기서는 도메인 업무 규칙을 구현하지 않는다. 각 도메인이 router.py를 갖게 되면
아래처럼 include_router로만 연결한다.

    from app.domains.users.router import router as users_router
    api_router.include_router(users_router, prefix="/users", tags=["users"])

## 계층 경계 (app/domains/{domain}/ 내부)

    Router → Service → Repository → Database
               ↓
          Domain policy

- model.py: 영속성 구조 (SQLAlchemy ORM)
- schema.py: Pydantic 요청/응답 계약 (ORM 컬럼을 그대로 노출하지 않는다)
- repository.py: DB 질의
- service.py: 업무 규칙과 transaction 경계
- router.py: HTTP 입력/출력과 status code

필요한 파일만 만든다. 단순 조회에 불필요한 추상화를 강제하지 않되, router에서
복잡한 ORM 질의를 직접 작성하지 않는다.

## Router 등록 규칙

- tag는 도메인 이름을 그대로 쓴다 (예: `tags=["users"]`).
- 경로는 복수형 명사 기준 REST 스타일을 따른다 (`GET /users`, `GET /users/{id}`).
- 목록 응답은 `app.api.schemas.Page`(page/size/total/items)를 쓴다.
- 오류 응답은 `app.api.schemas.COMMON_ERROR_RESPONSES`를 `responses=`에 병합한다.
"""

from fastapi import APIRouter

from app.domains.users.router import router as users_router

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
