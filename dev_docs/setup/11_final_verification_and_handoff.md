# 11단계 — 최종 검증과 팀원 기능 개발 인계

## 목표

공통 세팅이 기능 개발 착수에 충분한지 최종 판정하고 팀원별 선결 의존성을 명확히 한다.

## 전체 검증 시나리오

1. 깨끗한 clone을 가정해 `.env`를 생성한다.
2. Docker image를 build한다.
3. DB와 API를 기동한다.
4. migration을 head까지 적용한다.
5. seed를 두 번 실행한다.
6. health/readiness와 OpenAPI를 확인한다.
7. lint, format, type, test를 실행한다.
8. ingredient 생성·조회·soft delete에 필요한 공통 DB 규칙을 확인한다.
9. 컨테이너를 일반 종료한 뒤 재기동하여 DB 데이터가 보존되는지 확인한다.
10. GitHub Actions 결과를 확인한다.
11. `app/core`, `app/domains`, `app/batch`가 유지되고 책임이 섞이지 않았는지 확인한다.
12. 최상위 `app/models`, `app/services`, `app/repositories`, `app/schemas`가 생성되지 않았는지 확인한다.

## 최종 명령 예시

```bash
docker compose up -d --build
docker compose run --rm api alembic upgrade head
docker compose run --rm api python -m app.db.seed
docker compose run --rm api python -m app.db.seed
docker compose exec api ruff check .
docker compose exec api ruff format --check .
docker compose exec api mypy app
docker compose exec api pytest -q
docker compose ps
```

## 기능 개발 착수 게이트

| 게이트 | 기준 |
|---|---|
| 실행 | 새 clone에서 API와 DB가 기동됨 |
| DB | 8개 MVP 테이블 migration 성공 |
| 데이터 | Seed로 실데이터 의존 없이 개발 가능 |
| 계약 | 공통 오류·pagination·현재 사용자 경계 확정 |
| 품질 | 로컬 및 CI 검사 통과 |
| 안전 | 비밀값·개인 경로·운영 데이터 미포함 |
| 구조 | 기존 도메인 중심 구조와 batch/core 책임 보존 |

## 팀원별 인계 항목

### 재성

- ingredient/product/profile 모델과 Mock 데이터
- 식재료 등록/상세 API가 사용할 Service/Repository 경계
- 카메라 인식 결과를 등록 요청으로 변환하는 계약

### 선영

- ingredient 목록/soft delete 규칙
- device와 notification 모델
- 유통기한 조회 인덱스와 알림 대상 계산에 필요한 Seed

### 우희

- users 모델과 current-user dependency 계약
- 인증 전 Mock identity 교체 지점
- 비밀번호 정책 결정 필요 항목

각 인계 문서에는 담당 도메인 경로, 공통 계층 변경이 필요한 상황, batch 연계 여부를 명시한다.

## 최종 산출물

- 공통 세팅 변경 요약
- 환경변수 목록
- DB migration revision
- Seed 데이터 설명
- API 공통 규약
- 로컬 실행 명령
- CI 링크와 결과
- 알려진 제한사항

## 완료 조건

- 팀원들이 다른 팀원 기능의 완성을 기다리지 않고 자기 기능을 시작할 수 있다.
- 실제 OCR/정제 데이터가 도착하면 Mock adapter만 교체할 수 있다.
- 미결정 정책은 숨기지 않고 backlog와 담당자를 기록했다.

## AI 지시문

```text
공통 세팅 전체를 깨끗한 환경 기준으로 검증해.
기존 app/core, app/domains, app/batch 보존과 도메인 내부 계층 배치를 별도 항목으로 검사해.
새 기능은 추가하지 말고 실패 원인을 공통 기반 범위에서만 수정해.
최종적으로 팀원별 개발 가능/불가능 항목과 남은 선결조건을 표로 보고해.
```
