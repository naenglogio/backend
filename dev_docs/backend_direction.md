# NaengLog Backend 개발 방향

## 1. 문서 목적

이 문서는 NaengLog 백엔드를 세 팀원이 AI IDE와 함께 개발할 때 공통으로 적용하는 최상위 지침이다. AI에게 기능 구현을 지시할 때 이 문서를 먼저 제공하고, 담당자 폴더의 기능별 문서를 함께 제공한다.

## 2. 기술 스택

- Python 3.12
- FastAPI
- Pydantic v2 및 pydantic-settings
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- pytest 및 httpx
- Ruff와 타입 검사 도구
- Docker 및 Docker Compose
- Firebase Admin SDK

패키지 버전은 호환성을 확인한 뒤 lock 파일에 고정한다.

## 3. MVP 시스템 경계

```text
React Frontend
    ↓ HTTPS/JSON
FastAPI Backend
    ↓ SQLAlchemy
PostgreSQL: 서비스 최종 데이터 8개 테이블
```

데이터 정제 파이프라인은 Backend와 분리한다.

```text
컬리 OCR JSON/CSV + 식약처 기준 CSV/Parquet
→ 공통 Docker 정제 파이프라인
→ load_ready.csv
→ DB Loader
→ products, product_freshness_profiles
```

Backend는 상세페이지 크롤링, OCR 실행, 식약처 PDF 파싱을 수행하지 않는다.

## 3.1 병렬 개발과 임시 가데이터 원칙

백엔드 개발은 크롤링·OCR·정제 파이프라인 완료를 기다리지 않고 병렬로 진행한다.

```text
백엔드
→ Mock 상품·소비기한 데이터로 API와 도메인 로직 구현

데이터 파이프라인
→ 실제 load_ready.csv 생성과 DB Loader 구현

양쪽 완료
→ Mock 데이터 제거
→ 실제 products·product_freshness_profiles 연결
→ 통합 테스트
```

파이프라인 완료 전에는 `dev_docs/mock_data_policy.md`의 계약을 사용한다.

- 가데이터는 실제 ERD 및 API 계약과 동일한 필드·타입·enum을 사용한다.
- 가데이터 전용 컬럼이나 임시 테이블을 만들지 않는다.
- production 코드에 하드코딩하지 않고 fixture, seed, factory 또는 fake adapter로 격리한다.
- 실제 데이터가 들어와도 Router와 Service 계약을 바꾸지 않도록 설계한다.
- 실제 데이터 준비 여부를 이유로 사용자·식재료·알림 개발을 중단하지 않는다.
- Mock을 실제 데이터로 오해하지 않도록 이름과 실행 환경을 명확히 표시한다.

## 4. MVP 데이터베이스

구현 대상은 다음 8개 테이블이다.

| 테이블                       | 역할                            |
| ---------------------------- | ------------------------------- |
| `users`                      | 사용자, 권한, 약관 및 알림 동의 |
| `user_devices`               | FCM 디바이스 토큰               |
| `categories`                 | 표준 식품 카테고리              |
| `foods`                      | 표준 식재료 Master              |
| `products`                   | 최종 정제 상품                  |
| `product_freshness_profiles` | 최종 소비기한·보관방법 프로필   |
| `ingredients`                | 사용자 냉장고 식재료            |
| `notifications`              | 소비기한 알림 이력              |

`raw_products`, `shelf_life_reference`는 서비스 DB에 만들지 않는다.

## 5. 공통 아키텍처 규칙

```text
Router
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy Session / ORM Model
  ↓
PostgreSQL
```

- Router: HTTP 입력, 인증 dependency, 응답 모델과 status code
- Service: 유스케이스, 권한, 도메인 검증과 transaction 조정
- Repository: 데이터 조회·저장 query
- ORM Model: DB 구조와 관계
- Pydantic Schema: API 요청·응답 계약
- Integration Adapter: Firebase, 지도, 레시피, AI API

## 6. 공통 개발 규칙

1. 작업 전에 현재 트리, dependency, migration과 관련 코드를 확인한다.
2. 한 번에 하나의 bounded task만 구현한다.
3. Router에 비즈니스 로직이나 직접 SQL을 넣지 않는다.
4. Repository에서 임의로 commit하지 않는다.
5. 사용자 소유 데이터는 `current_user.id`로 소유권을 검증한다.
6. ORM 모델과 API 스키마를 분리한다.
7. 모든 기능 변경에 관련 테스트를 추가한다.
8. 비밀번호, JWT secret, Firebase credential을 커밋하거나 로그에 출력하지 않는다.
9. 공유된 기존 migration을 수정하지 않고 새 migration을 추가한다.
10. 기존 팀원의 변경사항을 삭제하거나 되돌리지 않는다.

## 7. 금지 사항

명시적인 팀 합의 없이 다음을 추가하거나 변경하지 않는다.

- SNS 로그인
- Redis, Kafka, Celery
- Kubernetes와 MSA
- Raw OCR·식약처 원문 DB 테이블
- 챗봇 대화 이력 테이블
- 자체 레시피 DB
- 카메라 인식 로그·임베딩 테이블
- 디바이스별 FCM 발송 이력 테이블
- 사용자 식재료 물리 삭제
- 기존 API의 파괴적 변경

## 8. 공통 도메인 규칙

- `product_freshness_profiles.shelf_life_days`는 상대적인 일수다.
- `ingredients.expiration_date`는 사용자의 실물 식재료에 적용된 날짜다.
- 제조일을 모르는 `제조일로부터 N일` 값은 구매일에 더해 확정값으로 저장하지 않는다.
- 시스템 추정값은 `ESTIMATED`로 표시한다.
- 식재료 삭제는 `is_deleted = true`로 처리한다.
- 삭제할 때 `deletion_reason`은 필수다.
- 삭제 전용 일시 컬럼 없이 `updated_at`을 사용한다.
- 삭제된 식재료는 기본 목록, 알림, 추천 대상에서 제외한다.

## 9. 역할 분담

| 담당자 | 담당 기능                                 | 문서 위치             |
| ------ | ----------------------------------------- | --------------------- |
| 재성   | 메인 3D, 카메라 인식, 식재료 등록·상세    | `dev_docs/jaeseong/`  |
| 선영   | 식재료 목록, 알림, 주변 마트, 맞춤 레시피 | `dev_docs/seonyoung/` |
| 우희   | 회원가입·로그인, 내정보, AI 챗봇          | `dev_docs/woohee/`    |

## 10. 공통 API Prefix와 응답

- Prefix: `/api/v1`
- 인증: `Authorization: Bearer <access_token>`
- 날짜: `YYYY-MM-DD`
- datetime: ISO 8601 UTC
- 목록 API: pagination 사용

오류 응답 예시:

```json
{
  "code": "INGREDIENT_NOT_FOUND",
  "message": "식재료를 찾을 수 없습니다.",
  "details": null
}
```

## 11. AI 완료 보고 형식

```text
결과:
- 구현한 기능

변경 파일:
- path: 변경 이유

DB 변경:
- migration 이름 또는 없음

검증:
- 실행한 명령
- 성공 또는 실패 결과

남은 사항:
- 후속 작업 또는 없음
```

## 12. 공통 완료 조건

- 요구사항 충족
- migration과 ORM 일치
- 권한과 소유권 검증
- 논리 삭제 정책 준수
- pytest 통과
- Ruff 통과
- 타입 검사 통과
- OpenAPI 요청·응답 확인
- 관련 문서와 테스트 갱신
- 파이프라인 의존 기능은 Mock 데이터 테스트 또는 실제 데이터 통합 테스트 중 현재 단계에 맞는 검증 완료
