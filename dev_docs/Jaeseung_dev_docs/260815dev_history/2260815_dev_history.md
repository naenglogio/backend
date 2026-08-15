# 2026-08-15 개발 기록 — BE-1

- 브랜치: `feat/ingredients`
- 테스크: BE-1 (ingredients 모델 정본화 + 마이그레이션)
- 기준 문서: `backend/10_be_model_migration.md`, `shared/00_API_CONTRACT.md`

## 목적

기존 `ingredients` 스키마를 노션 ERD #7 / API 계약서 정본에 맞춘다.
프론트가 FE-0/FE-1(타입·API 클라이언트)까지 끝난 상태라, BE 실연동의 출발점이 되는 스키마를 확정한다.

## 한 일

### 1. 모델 정본화 (`app/domains/ingredients/model.py`)

**추가 필드**
| 필드 | 타입 | 비고 |
|------|------|------|
| `name` | varchar(255), NOT NULL | 화면 표시용 이름 |
| `quantity` | int, NOT NULL, default 1 | 수량 |
| `unit` | varchar(30), NULL | 단위 |
| `purchase_date` | date, NULL | 구매일 |
| `image_url` | text, NULL | 이미지 URL |
| `memo` | text, NULL | 메모 |

**수정 필드**
- `storage_type`: 문자열 enum(`REFRIGERATED`/`FROZEN`/`ROOM_TEMPERATURE`) → **int (0=냉장, 1=냉동)**
  - `ROOM_TEMPERATURE` 제거
  - CHECK: `storage_type IN (0, 1)`
- `expiration_date`: NOT NULL → **nullable** (계약서 정본)
- `deletion_reason`: `WRONG_ENTRY` → **`INCORRECT_ENTRY`**
- soft delete CHECK 유지 (`is_deleted` ↔ `deletion_reason`)

### 2. Enum 정리

- `app/domains/ingredients/enums.py`
  - `DeletionReason.INCORRECT_ENTRY` 로 변경
- `app/domains/freshness/enums.py`
  - `StorageType` 문자열 enum은 **product_freshness_profiles용으로 유지**
  - ingredients는 int를 쓰므로 이 enum을 쓰지 않음 (주석으로 명시)

### 3. Alembic 마이그레이션

- 파일: `alembic/versions/a1b2c3d4e5f6_align_ingredients_with_notion_erd.py`
- down_revision: `92a7ff678da3` (nickname)
- upgrade 요지:
  1. `storage_type` 값 변환 후 smallint로 변경
  2. `WRONG_ENTRY` → `INCORRECT_ENTRY`
  3. 누락 컬럼 추가 (`name`은 기존 행을 `foods.name`으로 백필 후 NOT NULL)
  4. `expiration_date` nullable
- downgrade도 작성함

> 로컬 Docker에서 `alembic upgrade head` 적용은 각자 환경에서 수행.
> migration **파일**은 Git으로 공유하고, DB 데이터 자체는 push되지 않음.

### 4. Seed 최소 수정 (모델 깨짐 방지)

- `app/db/seed/data.py`: ingredients seed를 int `storage_type` / `name` / `INCORRECT_ENTRY`에 맞춤
- `app/db/seed/runner.py`: Ingredient 생성 시 새 필드 전달
- 본격 seed 정리는 BE-6 범위

### 5. 진행판 갱신

- `shared/01_STATUS_BOARD.md` BE-1 → ✅
- 프론트에 알릴 내용: ingredients 스키마가 계약서대로 확정됨

## 변경 파일 목록

| 파일 | 내용 |
|------|------|
| `app/domains/ingredients/model.py` | 스키마 정본화 |
| `app/domains/ingredients/enums.py` | `INCORRECT_ENTRY` |
| `app/domains/freshness/enums.py` | StorageType 사용 범위 주석 |
| `alembic/versions/a1b2c3d4e5f6_*.py` | migration (신규) |
| `app/db/seed/data.py` | seed 데이터 맞춤 |
| `app/db/seed/runner.py` | seed 생성 로직 맞춤 |
| `dev_docs/.../01_STATUS_BOARD.md` | BE-1 ✅ |

## 체크포인트

- [x] 노션 Ingredient 필드 반영 (타입·nullable·default)
- [x] `storage_type` int(0/1), ROOM_TEMPERATURE 제거
- [x] `deletion_reason` = `INCORRECT_ENTRY`
- [x] soft delete CHECK 유지
- [ ] 로컬에서 migration up/down 검증 (Docker 기동 후 확인 필요)

## 다음

- BE-2: ingredients 도메인 뼈대 (`schema` / `repository` / `service` / `router`)
- 그다음 BE-3(목록·상세) → FE-2/FE-6 실연동 가능
