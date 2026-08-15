# BE-1. ingredients 모델 정본화 + 마이그레이션

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (Ingredient 필드표)
- 현재 `app/domains/ingredients/model.py`, `app/domains/ingredients/enums.py`, `app/domains/freshness/enums.py`
- `dev_docs/mock_data_policy.md`

## 지시
현재 `ingredients` 모델을 **노션 ERD #7 정본**대로 완성하고 Alembic 마이그레이션을 생성하라.

### 추가할 누락 필드
`name`(varchar255, not null), `quantity`(int, not null, default 1), `unit`(varchar30, null), `purchase_date`(date, null), `image_url`(text, null), `memo`(text, null)

### 수정할 필드
- `storage_type`: 현재 문자열 enum 3종(REFRIGERATED/FROZEN/**ROOM_TEMPERATURE**) → **int(0 냉장 / 1 냉동)**. ROOM_TEMPERATURE는 노션에 없으므로 제거.
- `deletion_reason` enum: 현재 `WRONG_ENTRY` → **`INCORRECT_ENTRY`** (노션 정본).

### 유지할 필드 (이미 정본과 일치)
`expiration_source`(USER_INPUT/PACKAGE_OCR/PRODUCT_DISCLOSURE/MFDS_REFERENCE, default USER_INPUT), `expiration_status`(CONFIRMED/ESTIMATED/REVIEW_REQUIRED, default CONFIRMED), `is_deleted`, FK들, soft delete CHECK 제약.

## 체크포인트
- [ ] 노션 Ingredient 필드가 타입·nullable·default까지 전부 반영됐는가
- [ ] storage_type이 int(0/1)이고 ROOM_TEMPERATURE가 제거됐는가
- [ ] deletion_reason이 INCORRECT_ENTRY인가
- [ ] soft delete CHECK 제약(`is_deleted=false ↔ deletion_reason IS NULL`)이 유지되는가
- [ ] 마이그레이션 up/down이 정상 동작하는가

## 완료 후
`../shared/01_STATUS_BOARD.md`의 BE-1 → ✅.
프론트에 알릴 것: ingredients 스키마가 계약서대로 확정됨 → FE가 목업에서 실연동으로 전환 가능해지는 출발점.
