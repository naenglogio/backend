# 5단계 — MVP ORM 모델과 최초 migration

## 목표

팀원 기능이 공통으로 의존하는 MVP 8개 테이블을 ORM과 migration으로 확정한다.

## MVP 테이블

| 테이블 | 핵심 역할 | 주요 연관 |
|---|---|---|
| `users` | 계정과 알림 동의 | devices, ingredients, notifications |
| `devices` | 사용자별 푸시 토큰 | users |
| `categories` | 표준 식품 분류 | foods |
| `foods` | 일반화된 식품 마스터 | categories, products, ingredients, profiles |
| `products` | 컬리N마트 상품 식별 | foods, profiles, ingredients |
| `product_freshness_profiles` | 정제된 보관·소비기한 결과 | foods, products, ingredients |
| `ingredients` | 사용자 냉장고 식재료 | users, foods, products, profiles |
| `notifications` | 알림 내역 | users, ingredients |

## 필수 도메인 규칙

- `ingredients.product_id`, `freshness_profile_id`는 직접 입력 식재료를 위해 nullable이다.
- `ingredients.is_deleted` 기본값은 `false`다.
- `ingredients.deletion_reason`은 활성 상태에서는 `null`, 삭제 상태에서는 `CONSUMED`, `DISCARDED`, `WRONG_ENTRY` 중 하나다.
- 별도 삭제일시는 만들지 않고 `updated_at`을 사용한다.
- 사용자 삭제는 soft delete이며 일반 목록 조회는 `is_deleted = false`를 기본으로 한다.
- `expiration_source`: `USER_INPUT`, `PACKAGE_OCR`, `PRODUCT_DISCLOSURE`, `MFDS_REFERENCE`.
- `expiration_status`: `CONFIRMED`, `ESTIMATED`, `REVIEW_REQUIRED`.
- 최종 정제 테이블에는 처리 중간 JSON 전체를 저장하지 않는다. 원문 파일과 중간 산출물은 데이터 파이프라인 저장소의 책임이다.
- 가격은 서비스 요구사항이 아니므로 products에 가격 컬럼을 추가하지 않는다.

## 모델 배치 원칙

```text
app/domains/
├─ users/model.py
├─ devices/model.py
├─ categories/model.py
├─ foods/model.py
├─ products/model.py
├─ freshness/model.py
├─ ingredients/model.py
└─ notifications/model.py
```

각 모델은 자기 도메인에 위치한다. 공통 `Base`와 DB 세션만 `app/db`를 사용하며, 최상위 `app/models` 폴더는 만들지 않는다. 관계 때문에 발생하는 순환 import는 문자열 관계 선언과 중앙 model registry로 해결한다.

## 구현 작업

1. 테이블별 ORM 모델과 Python Enum 또는 DB 제약 전략을 작성한다.
2. 모든 FK의 nullable과 delete 정책을 명시한다.
3. 조회 패턴 기반 인덱스를 추가한다.
   - `ingredients(user_id, storage_type, expiration_date)`
   - `ingredients(user_id, is_deleted)`
   - device token unique
   - product external identifier unique
   - profile의 product/food 및 상태 조회 인덱스
4. 최초 Alembic revision을 자동 생성한 뒤 반드시 수동 검토한다.
5. upgrade와 downgrade를 모두 실행 검증한다.
6. Alembic model registry가 8개 도메인 모델을 모두 가져오는지 확인한다.

## 모델 작성 시 확인할 항목

- 현재 Notion ERD 또는 승인된 DBML이 이 문서와 다르면 구현을 중단하고 ERD를 우선한다.
- Enum을 PostgreSQL native enum으로 만들지 문자열+check로 만들지 한 방식으로 통일한다.
- 사용자 email과 device token의 unique 정책을 확인한다.
- 알림 삭제 정책은 사용자/식재료 삭제와 충돌하지 않게 한다.

## 검증

```bash
docker compose up -d db
docker compose run --rm api alembic upgrade head
docker compose run --rm api alembic current
docker compose run --rm api alembic downgrade base
docker compose run --rm api alembic upgrade head
```

추가로 실제 DB의 테이블, FK, unique, index가 migration과 일치하는지 조회한다.

## 완료 조건

- 8개 테이블이 migration으로 생성된다.
- 모든 관계와 인덱스가 승인 ERD와 일치한다.
- downgrade 후 재-upgrade가 성공한다.
- ORM import 순환 문제가 없다.

## AI 지시문

```text
승인된 MVP ERD를 기준으로 8개 ORM 모델과 최초 Alembic migration을 구현해.
모델은 app/domains/{domain}/model.py에 배치하고 기존 app/domains 구조를 유지해.
필드나 테이블을 편의상 추가하지 말고, 특히 가격·원문 OCR JSON·삭제일시는 만들지 마.
ingredients soft delete 규칙과 deletion_reason 무결성을 DB 또는 애플리케이션 계층에서 명시적으로 보장해.
upgrade/downgrade를 실제 빈 로컬 DB에서 검증해.
```
