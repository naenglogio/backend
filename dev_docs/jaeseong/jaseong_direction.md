# 재성 담당 Backend 개발 방향

## 담당 범위

- 메인 화면 3D 냉장고 데이터 제공
- 식재료 카메라 인식 API 연결
- 식재료 등록
- 식재료 상세 조회 및 수정

## 주요 테이블

- `categories`
- `foods`
- `products`
- `product_freshness_profiles`
- `ingredients`

## 주요 API

```text
GET    /api/v1/categories
GET    /api/v1/foods
GET    /api/v1/foods/{food_id}
GET    /api/v1/products
GET    /api/v1/products/{product_id}
POST   /api/v1/ingredients
GET    /api/v1/ingredients/{ingredient_id}
PATCH  /api/v1/ingredients/{ingredient_id}
POST   /api/v1/recognition/candidates
```

## 협업 경계

- 식재료 목록과 논리 삭제는 선영과 `ingredients` API 계약을 공유한다.
- 사용자 인증은 우희가 구현한 `current_user` dependency를 사용한다.
- 소비기한 프로필은 공통 DB Loader가 적재하며 재성 기능에서 직접 생성하지 않는다.
- 카메라 결과는 후보만 반환하고 사용자가 확인한 뒤 식재료를 등록한다.

## 구현 우선순위

1. categories·foods·products 조회
2. 식재료 직접 등록
3. 상품 기반 식재료 등록
4. 상세 조회와 수정
5. 카메라 인식 adapter
6. 3D 냉장고 응답 최적화

