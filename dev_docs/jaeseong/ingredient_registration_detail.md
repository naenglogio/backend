# 식재료 등록·상세 개발 지시서

## 목표

사용자가 직접 입력하거나 컬리 상품을 선택하여 식재료를 등록하고, 등록된 식재료의 상세정보를 조회·수정한다.

## 등록 입력

```text
food_id
product_id?
freshness_profile_id?
name
storage_type
quantity
unit?
purchase_date?
expiration_date?
expiration_source
expiration_status
image_url?
memo?
```

## 검증 규칙

- `quantity >= 0`
- 사용자는 자기 계정에만 식재료를 등록한다.
- `product_id`가 있으면 상품의 `food_id`와 입력 `food_id`가 같아야 한다.
- `freshness_profile_id`가 있으면 profile의 `product_id`가 입력 `product_id`와 같아야 한다.
- 사용자 직접 입력 소비기한은 `USER_INPUT`으로 저장한다.
- 시스템 보완값은 `ESTIMATED` 상태를 사용한다.
- 제조일이 불명확하면 권장 일수로 확정 날짜를 자동 생성하지 않는다.

## AI 구현 지시문

```text
backend_direction.md와 jaseong_direction.md를 먼저 읽고 ingredients 등록·상세 기능만 구현하라.

범위:
- POST /api/v1/ingredients
- GET /api/v1/ingredients/{ingredient_id}
- PATCH /api/v1/ingredients/{ingredient_id}
- request/response schema
- repository와 service
- 인증 사용자 소유권 검증
- food/product/profile 일관성 검증
- 단위·API 테스트

Router-Service-Repository 경계를 지켜라.
다른 사용자의 ingredient를 조회하거나 수정할 수 없게 하라.
논리 삭제된 ingredient의 상세·수정 허용 정책을 명시하고 테스트하라.
알림, 목록, 삭제, 카메라 모델은 이번 작업에서 구현하지 마라.

실제 products와 product_freshness_profiles 데이터가 아직 없으면 mock_data_policy.md의 fixture를 사용하라.
Mock 전용 분기나 임시 DB 테이블을 만들지 말고 동일한 ORM과 API 계약으로 테스트하라.

먼저 기존 구조와 migration을 확인하고 영향 파일을 제시한 뒤 구현하라.
```

## 완료 조건

- 직접 등록과 상품 기반 등록 테스트
- 잘못된 food/product/profile 조합 차단
- 타 사용자 접근 차단
- 날짜·상태 규칙 테스트
- OpenAPI 요청·응답 확인
- Mock 상품 기반 테스트 후 실제 적재 데이터로 교체 가능한 구조 확인
