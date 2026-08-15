# BE-4. 등록 API

## 선행
BE-2 완료.

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (3. 등록)
- 노션 7항 소비기한 규칙

## 지시
```
POST /api/v1/ingredients
```
- 요청: `IngredientCreateRequest`
- 직접입력(product_id/freshness_profile_id null) 지원.
- 검증: 필수값, quantity 양수, 날짜 형식. 실패 시 422(`{code,message,details}`).
- 기본값: `expiration_source=USER_INPUT`, `expiration_status=CONFIRMED`.
- **소비기한 규칙**: 기준일(제조일→포장일→구매일→수령일→등록일 우선순위) + shelf_life_days = expiration_date. 제조일 불명 + 고시가 "제조일로부터 N일"이면 확정 금지 → `expiration_status=ESTIMATED`.
- 응답: 생성된 `Ingredient`.

## 체크포인트
- [ ] 직접입력 등록 성공(product 없이)
- [ ] default 값이 노션대로
- [ ] ESTIMATED 분기 동작
- [ ] 검증 실패 422 + 필드별 details
- [ ] 응답이 상세 스키마와 동일

## 완료 후
`../shared/01_STATUS_BOARD.md`의 BE-4 → ✅.
프론트에 알릴 것: **등록 화면(FE-3)이 실연동 가능**해짐.
