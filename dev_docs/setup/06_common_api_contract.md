# 6단계 — 공통 API 계약과 계층 경계

## 목표

팀원들이 서로 다른 응답·오류·DB 접근 방식을 만들지 않도록 API 공통 규약을 고정한다.

## 권장 계층

```text
Router → Service → Repository → Database
           ↓
      Domain policy
```

- Router: HTTP 입력/출력과 status code
- Service: 업무 규칙과 transaction 경계
- Repository: DB 질의
- Schema: Pydantic 요청/응답 계약
- Model: 영속성 구조

단순 조회까지 불필요한 추상화를 강제하지 않되 Router에서 복잡한 ORM 질의를 직접 작성하지 않는다.

## 공통 규약

1. 버전 prefix는 `/api/v1`을 사용한다.
2. Pydantic 응답은 ORM 내부 컬럼을 그대로 노출하지 않는다.
3. 시간은 ISO 8601 형식으로 반환한다.
4. 목록 응답의 pagination 방식을 하나로 정한다. MVP는 `page`, `size`, `total`, `items` 방식이 이해하기 쉽다.
5. 오류는 `code`, `message`, `details` 구조를 따른다.
6. 삭제된 ingredient는 기본 조회에서 제외한다.
7. 인증 미구현 기간에는 사용자 ID를 코드에 하드코딩하지 않는다. 테스트용 dependency override나 명시적 mock identity를 사용한다.

## 공통 schema 예시

```python
class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, object] | None = None

class PageMeta(BaseModel):
    page: int
    size: int
    total: int
```

## 구현 작업

- 최상위 API router와 팀 기능 router 등록 위치를 만든다.
- DB session, 현재 사용자, pagination 공통 dependency 위치를 정한다.
- 공통 응답/오류 schema를 만든다.
- OpenAPI tag와 endpoint naming 규칙을 문서화한다.
- 아직 팀원 기능 endpoint는 구현하지 않는다.

## 완료 조건

- 새 Router를 한 곳에서 등록할 수 있다.
- OpenAPI 문서에서 `/api/v1` 경로와 오류 schema를 확인할 수 있다.
- 인증 구현 전후에 현재 사용자 dependency만 교체할 수 있다.

## AI 지시문

```text
팀 기능 자체는 구현하지 말고 공통 Router, schema, dependency 경계만 구성해.
인증을 가짜로 완성한 것처럼 만들지 말고 교체 가능한 current-user dependency 계약만 정의해.
샘플 endpoint가 필요하면 테스트 전용 또는 명확한 예제로 제한해.
```
