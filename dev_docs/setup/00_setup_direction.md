# 백엔드 공통 세팅 실행 지침

## 1. 목적

이 문서는 팀원별 기능 개발을 시작하기 전에 재성이 공통 백엔드 기반을 구축하는 전체 순서를 정의한다. 각 단계 문서는 AI IDE에 한 번에 하나씩 전달하는 독립 실행 지시서다.

기준 저장소: <https://github.com/naenglogio/backend>

확인 기준 커밋: `0d494b671d3fd8cf4a91d9c40ca7bd129165c1a9`

## 2. 현재 저장소 상태

- Python 3.12 이상, FastAPI, SQLAlchemy 2, PostgreSQL, Alembic 기반이다.
- Docker Compose에 PostgreSQL과 API 서비스가 정의되어 있다.
- API에는 `/health`만 존재한다.
- 설정은 `DATABASE_URL`만 읽는다.
- Alembic의 `target_metadata`가 `None`이라 모델 기반 migration 자동 생성이 불가능하다.
- DB Base/세션/ORM 모델, 공통 Router, 오류 규격, Mock/Seed, 테스트, CI가 아직 없다.
- PostgreSQL 이미지는 `pgvector/pgvector:pg16`이지만 MVP ERD에는 벡터 컬럼이 없다. 제거하지 말고 확장 단계 결정사항으로 남긴다.

## 3. 공통 원칙

1. 한 번에 한 단계만 구현한다.
2. 이전 단계의 검증 명령이 모두 통과한 뒤 다음 단계로 이동한다.
3. 기존 `dev_docs/backend_direction.md`와 팀원별 문서를 기능 요구사항의 상위 기준으로 사용한다.
4. 크롤링·OCR·정제 파이프라인이 완료되기 전에는 공통 Mock/Seed 데이터를 사용한다.
5. 상품·소비기한 데이터 계약을 임의 변경하지 않는다.
6. 애플리케이션 런타임은 `asyncpg`, Alembic migration은 현재 구성대로 `psycopg`를 사용한다.
7. 비밀값과 실제 `.env`는 커밋하지 않는다.
8. 각 단계 완료 시 변경 파일, 설계 결정, 실행 명령, 테스트 결과, 남은 위험을 보고한다.

## 4. 실행 순서

| 순서 | 문서 | 완료 결과 |
|---:|---|---|
| 1 | `01_repository_baseline.md` | 현재 상태 기록과 구현 경계 확정 |
| 2 | `02_dependencies_and_quality.md` | 개발 의존성과 정적 검사 도구 정립 |
| 3 | `03_application_core.md` | 환경설정·로깅·예외·상태 확인 기반 |
| 4 | `04_database_foundation.md` | Async DB 세션·Base·Alembic 연결 |
| 5 | `05_mvp_models_and_migration.md` | MVP 8개 테이블과 최초 migration |
| 6 | `06_common_api_contract.md` | 공통 Router·응답·오류·의존성 규칙 |
| 7 | `07_mock_and_seed_data.md` | 기능 개발용 가데이터와 seed 명령 |
| 8 | `08_test_foundation.md` | 단위·통합 테스트 기반 |
| 9 | `09_docker_local_operation.md` | 팀 공통 로컬 실행 절차 |
| 10 | `10_ci_and_collaboration.md` | GitHub Actions와 협업 품질 기준 |
| 11 | `11_final_verification_and_handoff.md` | 기능 개발 착수 가능 여부 판정 |

## 5. 단계별 AI 실행 방식

각 문서를 AI IDE에 제공하고 다음처럼 지시한다.

```text
현재 저장소를 먼저 분석한 뒤, 첨부한 단계 문서의 범위만 구현해.
이미 존재하는 사용자 변경사항은 보존하고, 범위 밖 리팩터링은 하지 마.
문서의 검증 명령을 실행하고 결과를 완료 보고 형식으로 정리해.
결정이 필요한 항목이나 기존 구조와 충돌하는 항목은 임의로 처리하지 말고 먼저 질문해.
```

## 6. 중단 조건

- 실제 ERD와 `backend_direction.md`의 MVP 테이블 정의가 충돌하는 경우
- Docker 또는 PostgreSQL 포트를 변경해야 하는 경우
- 인증 방식이나 비밀번호 해시 정책이 아직 결정되지 않은 경우
- 기존 팀원 작업 파일을 덮어써야 하는 경우
- 테스트를 통과시키기 위해 기능 요구사항을 축소해야 하는 경우

## 7. 공통 완료 보고 형식

```markdown
## 완료 범위
## 변경 파일
## 핵심 설계 결정
## 실행한 검증 명령과 결과
## 미완료 또는 위험 요소
## 다음 단계 진행 가능 여부
```
