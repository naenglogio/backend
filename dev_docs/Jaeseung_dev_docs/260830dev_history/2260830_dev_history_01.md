# 2026-08-30 개발 기록 — BE-3 (목록/상세 조회 API)

- 브랜치: `feat/ingredients`
- 테스크: BE-3 (목록/상세 조회 API)
- 기준 문서: `backend/12_be_list_detail_api.md`, `shared/00_API_CONTRACT.md`
- 선행: BE-1(모델/마이그레이션), BE-2(도메인 뼈대) 완료 상태에서 시작

## 목적

`service.py`/`repository.py`에 `NotImplementedError`로 남아있던 목록·상세 조회를
실제 쿼리로 채운다. 목표는 계약서(`GET /ingredients`, `GET /ingredients/{id}`)대로
소유권 검증·필터·페이지네이션·연관 데이터(product/freshness_profile) 포함을 동작시키는 것.

## 한 일

### 1. `app/domains/ingredients/repository.py`

- `list_active_by_user`: `user_id` + `is_deleted=false` 조건에 `storage_type`,
  `expiration_status` optional 필터 추가. `func.count()`로 total 별도 조회,
  `created_at desc, id desc`로 정렬 후 offset/limit 페이지네이션.
- `get_owned_by_id`: 소유권(`user_id`) + `is_deleted=false` 조건으로 단건 조회.
  목록에서 이미 숨긴 소프트 삭제 항목은 상세에서도 동일하게 404 처리(가시성 일치).
- `get_product_by_id` / `get_freshness_profile_by_id`: 상세 응답에 붙일 연관 데이터 조회.

### 2. `app/domains/ingredients/service.py`

- `list_ingredients`: `(page-1)*size` offset 계산 후 repository 호출 → `Page[Ingredient]`로 포장.
- `get_ingredient_detail`: `get_owned_by_id` 결과 없으면 `IngredientNotFoundError`(404).
  `product_id`/`freshness_profile_id`가 있을 때만 연관 조회해 `IngredientDetailResponse`에 매핑.
  직접입력(둘 다 null)이면 `product`/`freshness_profile` 그대로 null.

### 3. `app/domains/ingredients/router.py` — 필터 버그 수정

BE-2에서 만든 `storage_type: Literal[0, 1] | None` 쿼리 타입이 실제로는 항상
검증 실패하는 걸 검증 중 발견. 쿼리 문자열("0"/"1")은 str로 들어오는데
pydantic v2의 `Literal[int, ...]`은 문자열→정수 강제변환을 하지 않아
`{"code":"VALIDATION_ERROR", ... "Input should be 0 or 1"}`로 항상 막힘.
→ `int | None` + `Query(ge=0, le=1)`로 교체. `service.list_ingredients`의
`storage_type` 파라미터 타입도 `int | None`로 맞춤(repository와 동일 타입).

## 검증 중 발견해 같이 고친 선행 버그 (BE-1/BE-2 잔재)

BE-3 자체 범위는 아니지만 이 상태로는 마이그레이션조차 못 올려서 검증이 불가능했음.
사용자 확인 후 수정.

1. **`alembic/versions/a1b2c3d4e5f6_*.py` — naming convention 이중 적용**
   `naming.py`에 `ck: ck_%(table_name)s_%(constraint_name)s` convention이 걸려 있는데
   `op.drop_constraint("ck_ingredients_storage_type", ...)`처럼 이미 완성된 이름을
   리터럴로 넘기면 Alembic이 그 이름을 다시 convention에 태워
   `ck_ingredients_ck_ingredients_storage_type`(존재하지 않는 이름)로 DROP을 시도해 실패.
   → 모든 `drop_constraint`/`create_check_constraint` 하드코딩 이름을 `op.f(...)`로 감쌈
   (upgrade/downgrade 양쪽, storage_type·deletion_reason 제약 전부).

2. **같은 마이그레이션 — `deletion_reason` 컬럼 폭 부족**
   기존 컬럼이 `WRONG_ENTRY`(11자) 기준 `VARCHAR(11)`이라 `INCORRECT_ENTRY`(15자)로
   UPDATE 시 `StringDataRightTruncation` 에러. → UPDATE 전에 `VARCHAR(16)`로 widen하는
   `op.alter_column` 추가(upgrade), downgrade에서는 데이터 원복 후 다시 11로 축소.

3. **`app/db/seed/data.py` / `runner.py` — `nickname` NOT NULL 누락**
   `users.nickname`이 NOT NULL인데 시드 데이터에 필드 자체가 없어 seed 실행이
   `NotNullViolationError`로 실패. → `SEED_USERS`에 `nickname` 필드 추가,
   `_get_or_create_user`가 이를 받아 `User` 생성 시 전달하도록 수정.

4. **Docker 이미지가 `python-multipart` 반영 전 상태로 stale**
   `pyproject.toml`엔 이미 있었지만 이미지가 그 전에 빌드된 상태라 컨테이너가
   기동 시점에 `RuntimeError: Form data requires "python-multipart"`로 죽어 있었음.
   → `docker compose build api` 재빌드로 해결(코드 변경 없음, 인프라 문제).

## 검증 (Docker + 실제 DB)

`docker compose up -d` → `alembic upgrade head`(up/down/up 왕복 확인) →
`python -m app.db.seed`로 시드 적재 → curl로 실제 호출.

| 시나리오 | 기대 | 결과 |
|---|---|---|
| user3 목록 조회 (active만) | 1건(우유) | ✅ |
| user4 목록 + `storage_type=0` | 당근 1건 | ✅ |
| user4 목록 + `storage_type=1` | 0건(냉동만두는 삭제됨) | ✅ |
| `storage_type=2` | 422 (`le=1` 위반) | ✅ |
| `expiration_status=ESTIMATED` 필터 | 당근 1건 | ✅ |
| `size=1&page=1` 페이지네이션 | `size:1, total:1` | ✅ |
| user3 상세(id=1, product+profile 있음) | 응답에 `product`/`freshness_profile` 채워짐 | ✅ |
| user5 상세(id=3, 직접입력) | `product`/`freshness_profile` null | ✅ |
| user4가 user3 소유(id=1) 조회 | 404 `INGREDIENT_NOT_FOUND` | ✅ |
| user3가 소프트삭제된 자기 항목(id=4) 조회 | 404 | ✅ |
| 인증 헤더 없이 목록 조회 | 401 `INVALID_TOKEN` | ✅ |

## 변경 파일 목록

| 파일 | 내용 |
|------|------|
| `app/domains/ingredients/repository.py` | 목록/상세/연관조회 쿼리 구현 |
| `app/domains/ingredients/service.py` | 목록/상세 유스케이스 구현, `StorageTypeInt` import 제거 |
| `app/domains/ingredients/router.py` | `storage_type` 쿼리 타입을 `Literal[0,1]`→`int(ge=0,le=1)`로 수정 |
| `alembic/versions/a1b2c3d4e5f6_*.py` | `op.f()` 누락, `deletion_reason` 컬럼 widen 버그 수정 |
| `app/db/seed/data.py` | `SEED_USERS`에 `nickname` 추가 |
| `app/db/seed/runner.py` | `_get_or_create_user`가 `nickname` 전달받도록 수정 |
| `shared/01_STATUS_BOARD.md` | BE-3 → ✅ |
| `dev_docs/.../260830dev_history/2260830_dev_history_01.md` | 본 기록 |

## 체크포인트 (backend/12_be_list_detail_api.md 기준)

- [x] 목록 필터·페이지네이션 동작
- [x] 소유권 404/403 일관 (남의 것/소프트삭제 모두 404)
- [x] 상세 응답에 product·freshness_profile 포함(직접입력 시 null)
- [x] 응답이 계약서·프론트 타입과 일치

## 다음

**BE-4**: 등록 API (`POST /ingredients`) — 기본값(`USER_INPUT`/`CONFIRMED`),
소비기한 규칙(기준일+shelf_life_days, 제조일 불명 시 ESTIMATED), 422 검증 구현.
