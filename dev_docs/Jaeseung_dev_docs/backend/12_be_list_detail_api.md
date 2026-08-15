# BE-3. 목록/상세 조회 API

## 선행
BE-2 완료.

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (1. 상세, 2. 목록)

## 지시
### 목록
```
GET /api/v1/ingredients?storage_type={0|1}&expiration_status={..}&page&size
```
- 소유분·`is_deleted=false`만. 필터는 optional.
- 응답: `Page[Ingredient]`

### 상세
```
GET /api/v1/ingredients/{id}
```
- 소유권 검증. 없거나 남의 것이면 404.
- 응답: `IngredientDetailResponse` = Ingredient + product(null 가능) + freshness_profile(null 가능).
- 직접입력(product_id null)이면 product/freshness_profile은 null.

## 체크포인트
- [ ] 목록 필터·페이지네이션 동작
- [ ] 소유권 404/403 일관
- [ ] 상세 응답에 product·freshness_profile 포함(직접입력 시 null)
- [ ] 응답이 계약서·프론트 타입과 일치

## 완료 후
`../shared/01_STATUS_BOARD.md`의 BE-3 → ✅.
프론트에 알릴 것: **상세 화면(FE-2)·3D 냉장고(FE-6)가 실연동 가능**해짐.
