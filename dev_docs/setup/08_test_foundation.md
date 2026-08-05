# 8단계 — 테스트 기반 구축

## 목표

팀원 기능이 추가될 때 공통 기반의 회귀를 즉시 탐지할 수 있게 한다.

## 권장 구조

```text
tests/
├─ conftest.py
├─ unit/
├─ integration/
├─ api/
└─ fixtures/
```

## 필수 테스트

1. 설정 로딩과 잘못된 설정 실패
2. `/health` 성공
3. `/ready` DB 정상/비정상
4. 공통 예외 응답 형식
5. Async session dependency 종료
6. migration head 적용
7. MVP 모델 관계와 주요 제약
8. ingredient soft delete 및 deletion reason 규칙
9. seed idempotency
10. API Router 등록과 OpenAPI 생성

## DB 테스트 전략

- production 또는 개인 로컬 DB를 테스트에 사용하지 않는다.
- Docker Compose의 별도 test database 또는 테스트 전용 database name을 사용한다.
- 테스트 간 데이터 격리는 transaction rollback 또는 schema 재생성 중 한 방법으로 통일한다.
- SQLite로 PostgreSQL 고유 제약과 타입을 대신 검증하지 않는다.

## 구현 작업

- AsyncClient 기반 FastAPI 테스트 client를 만든다.
- dependency override로 test DB와 mock user를 주입한다.
- fixture scope를 명확히 한다.
- migration 검증 테스트와 일반 unit test를 분리한다.
- 커버리지 수치보다 핵심 규칙 검증을 우선한다.

## 검증

```bash
pytest -q
pytest tests/unit -q
pytest tests/integration -q
```

## 완료 조건

- 테스트가 실행 순서에 의존하지 않는다.
- 개발 DB 데이터가 테스트로 변경되지 않는다.
- 실패 시 어느 계층에서 깨졌는지 알 수 있다.

## AI 지시문

```text
PostgreSQL 호환성을 유지하는 테스트 기반을 만들어.
실제 개발 DB를 사용하지 말고 테스트 DB와 dependency override를 사용해.
공통 기반, migration, soft delete, seed를 우선 검증하고 팀원 기능 테스트는 추가하지 마.
```
