# BE-5. 대시보드 집계 API

## 선행
BE-2 완료.

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (5. 집계)

## 지시
```
GET /api/v1/ingredients/summary
```
- 소유분·`is_deleted=false`만 집계.
- 응답: `IngredientSummaryResponse`
  - `total`: 전체 보유 수
  - `refrigerated_count`: storage_type=0
  - `frozen_count`: storage_type=1
  - `expiring_count`: 임박(D-day 이내) 수
  - `expiring_items`: 임박 목록 top N (`{id, name, storage_type, expiration_date}`)
- 임박 기준(D-day N일)은 상수로 정의하고 문서화.

## 체크포인트
- [ ] summary 응답이 계약서·프론트 타입과 일치
- [ ] 냉장/냉동 카운트 정확
- [ ] 임박 기준 명확·문서화
- [ ] 집계 쿼리가 repository에 있고 router는 위임만

## 완료 후
`../shared/01_STATUS_BOARD.md`의 BE-5 → ✅.
프론트에 알릴 것: **MainPage 대시보드 실연동(FE-5)이 가능**해짐.
