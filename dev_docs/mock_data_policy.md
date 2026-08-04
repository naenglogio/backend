# 데이터 파이프라인 완료 전 Mock 데이터 정책

## 1. 목적

컬리N마트 OCR과 식약처 기준 통합 파이프라인이 완료되기 전에도 Backend API, 도메인 규칙, 화면 연동과 테스트를 개발할 수 있도록 임시 가데이터 계약을 정의한다.

Mock 데이터는 실제 데이터를 대신하는 임시 개발 수단이며 서비스 운영 데이터가 아니다.

## 2. 적용 기간

```text
시작:
Backend 모델·API 개발 시작

종료:
load_ready.csv 계약 검증
+ DB Loader 적재 성공
+ 실제 데이터 통합 테스트 완료
```

실제 데이터 연동 완료 후에도 자동 테스트용 fixture와 factory는 유지할 수 있다. 개발용 seed를 운영 DB에 적재해서는 안 된다.

## 3. Mock 대상

- `categories`
- `foods`
- `products`
- `product_freshness_profiles`
- 알림 테스트용 `ingredients`
- 카메라 인식 후보
- 지도·레시피·AI·Firebase 외부 응답

사용자 인증과 소유권 검증은 가능한 한 실제 PostgreSQL 테스트 DB를 사용한다.

## 4. 금지 사항

- Mock 데이터를 위해 별도 DB 테이블 생성
- 실제 ERD에 없는 컬럼 추가
- production 코드에 상품 목록 하드코딩
- `if mock_mode:` 분기를 도메인 곳곳에 추가
- Mock 데이터를 실제 정제 결과라고 표시
- Mock 전용 API endpoint를 운영 OpenAPI에 노출
- 실제 데이터 적재 후 개발 seed를 운영 DB에 남김

## 5. 권장 저장 위치

```text
backend/
├─ tests/
│  ├─ factories/
│  └─ fixtures/
│     ├─ categories.json
│     ├─ foods.json
│     ├─ products.json
│     └─ freshness_profiles.json
└─ scripts/
   └─ seed_dev_data.py
```

- 테스트는 factory와 fixture를 우선 사용한다.
- 프론트엔드 연동이 필요한 로컬 환경에서만 `seed_dev_data.py`를 사용한다.
- seed script는 `APP_ENV=local` 또는 `test`에서만 실행되도록 보호한다.
- seed는 반복 실행해도 중복 row가 생기지 않게 작성한다.

## 6. 표준 Mock 상품 예시

```json
{
  "id": 1,
  "food_id": 101,
  "source_site": "KURLY_N_MART",
  "original_product_id": "MOCK-5047857",
  "name": "[MOCK] 한돈 삼겹살 600g",
  "product_url": "https://example.invalid/products/MOCK-5047857",
  "image_url": null,
  "is_active": true
}
```

Mock임을 식별할 수 있도록 다음 기준을 사용한다.

```text
original_product_id = MOCK-{식별값}
name = [MOCK] 접두어 사용
외부 URL = example.invalid 도메인
```

## 7. 표준 Mock 소비기한 프로필 예시

```json
{
  "id": 1,
  "product_id": 1,
  "storage_type": 0,
  "shelf_life_days": 7,
  "shelf_life_source": "PRODUCT_DISCLOSURE",
  "shelf_life_status": "CONFIRMED",
  "confidence_score": 0.98,
  "match_level": "FINE",
  "normalizer_version": "mock-0.1.0",
  "reference_version": "mock-2026-08"
}
```

## 8. 필수 시나리오 데이터

| 시나리오 | storage | 일수 | 상태 | 목적 |
|---|---:|---:|---|---|
| 냉장 확정값 | 0 | 7 | CONFIRMED | 컬리 고시정보 정상값 |
| 냉동 예상값 | 1 | 180 | ESTIMATED | 식약처 기준 보완값 |
| 프로필 없음 | 임의 | 없음 | 없음 | 사용자 직접 입력 |
| 비활성 상품 | 임의 | 임의 | 임의 | 검색 기본 제외 |
| 소비기한 임박 | 0 | 테스트 기준 | CONFIRMED | 알림 경계값 |

`REVIEW_REQUIRED`, `UNMATCHED`, `REJECTED`는 서비스 DB 적재 대상이 아니므로 상품 fixture로 저장하지 않는다. 이 상태는 데이터 파이프라인 테스트에서만 사용한다.

## 9. 실제 데이터 전환 조건

다음 조건을 모두 충족하면 실제 데이터 연동 단계로 전환한다.

- `load_ready.csv` 필수 컬럼과 enum 확정
- 샘플 파일 schema 검증 통과
- DB Loader dry-run 성공
- 동일 파일 재실행 멱등성 확인
- `products` upsert 성공
- `product_freshness_profiles` upsert 성공
- 실제 상품 조회 API 테스트 성공
- 상품 기반 ingredients 등록 테스트 성공
- 예상·확정 소비기한 UI/API 구분 확인

## 10. AI 구현 지시문

```text
크롤링·OCR·정제 파이프라인이 아직 완료되지 않았다.
mock_data_policy.md를 기준으로 실제 ERD 및 API 계약과 동일한 Mock fixture와 local seed를 작성하라.

필수 조건:
- 임시 테이블이나 Mock 전용 운영 API를 만들지 않는다.
- production service에 Mock 분기를 하드코딩하지 않는다.
- fixture, factory, fake adapter와 local seed로 격리한다.
- seed는 local/test 환경에서만 실행 가능해야 한다.
- seed는 멱등하게 작성한다.
- 실제 load_ready 데이터로 교체해도 Router·Service 계약이 변경되지 않게 한다.

먼저 필요한 시나리오와 파일 위치를 제시하고 승인된 범위만 구현하라.
```

