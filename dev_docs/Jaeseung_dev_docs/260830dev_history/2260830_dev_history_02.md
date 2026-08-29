# 2026-08-30 개발 기록 — BE-4 (등록 API)

- 브랜치: `feat/ingredients`
- 테스크: BE-4 (등록 API)
- 기준 문서: `backend/13_be_create_api.md`, `shared/00_API_CONTRACT.md` (3. 등록)
- 선행: BE-3(목록/상세) 완료 상태에서 시작

## 목적

`POST /ingredients`의 `NotImplementedError`를 실제 등록 로직으로 채운다.
직접입력(product 없이) 등록, 기본값, 소비기한 확정/추정 분기, FK 참조 검증을 구현.

## 한 일

### 1. `app/domains/ingredients/repository.py`

- `get_food_by_id` 추가: 등록 시 `food_id` 존재 확인용.
- `create` 구현: `session.add` + `flush`만 하고 commit은 service 경계로 넘김
  (기존 users 도메인 패턴과 동일).

### 2. `app/domains/ingredients/service.py`

- 새 도메인 에러 3종 추가 (전부 422): `FoodNotFoundError`, `ProductNotFoundError`,
  `FreshnessProfileNotFoundError`. FK가 깨진 요청이 DB IntegrityError로 500이
  되지 않도록 서비스 단에서 먼저 존재 확인.
- `create_ingredient`: food_id 확인 → (있으면) product_id 확인 → (있으면)
  freshness_profile_id 확인 및 조회 → `_resolve_expiration`으로 소비기한 계산 →
  `IngredientModel` 생성 → `repository.create` → `commit` → `refresh` →
  응답 스키마로 매핑.
- `_resolve_expiration` (소비기한 규칙 — 노션 7항을 현재 스키마로 근사):
  노션 규칙 원문은 기준일 우선순위를 **제조일→포장일→구매일→수령일→등록일**로
  두지만, BE-1에서 정본화된 `ingredients` 테이블에는 구매일(`purchase_date`)까지만
  있고 제조일/포장일/수령일 컬럼이 없다. 그래서 실제로는 아래 두 갈래로 구현:
  1. `expiration_date`를 요청에 직접 넣은 경우 → 그대로 확정(`CONFIRMED`)
     (포장지 등에서 실제 날짜를 읽어 입력한 경우로 간주).
  2. `freshness_profile_id`가 있는 경우 → 기준일(구매일, 없으면 등록일=오늘)
     + `profile.expiration_days`로 계산. 확정/추정 판단("제조일 불명 + 제조일
     기준 고시면 확정 금지")은 데이터 파이프라인이 프로필을 만들 때 이미
     반영해 `profile.expiration_status`로 내려주므로(BE-8 gold bundle import
     계약) 그대로 물려받음 — 별도 재판단하지 않음.
  3. 둘 다 없으면 확정할 근거가 없으므로 `ESTIMATED`, `expiration_date`는 null.

### 3. 검증(Docker, 실제 API 호출)

seed 데이터(BE-3에서 적재한 것 재사용, food_id=1 우유/product_id=1/freshness_profile_id=1,
`expiration_days=10`, `expiration_status=CONFIRMED`)에 대해 POST 호출.

| 시나리오 | 요청 요지 | 기대 | 결과 |
|---|---|---|---|
| 직접입력(날짜 없음) | `food_id`만, product/profile/expiration_date 없음 | `expiration_date=null`, `status=ESTIMATED` | ✅ |
| expiration_date 직접 입력 | 위 + `expiration_date="2026-09-10"` | 그대로 저장, `status=CONFIRMED` | ✅ |
| freshness_profile 기반 계산 | `product_id=1,freshness_profile_id=1,purchase_date="2026-08-01"` | `expiration_date=2026-08-11`(10일 후), `status=CONFIRMED`(profile 값 상속) | ✅ |
| `name` 누락 | — | 422 + `details`에 `loc:["body","name"]` | ✅ |
| `quantity=0` | — | 422 (`gt=0` 위반) | ✅ |
| 존재하지 않는 `food_id` | `food_id=999999` | 422 `FOOD_NOT_FOUND` (500 아님) | ✅ |
| 존재하지 않는 `product_id` | `product_id=999999` | 422 `PRODUCT_NOT_FOUND` | ✅ |
| 존재하지 않는 `freshness_profile_id` | `freshness_profile_id=999999` | 422 `FRESHNESS_PROFILE_NOT_FOUND` | ✅ |
| `storage_type=2` (JSON 바디) | — | 422 `literal_error`(0 or 1) — 바디는 JSON 네이티브 int라 BE-3의 쿼리 스트링 이슈 없음 | ✅ |
| 생성 후 상세 재조회(GET `/{id}`) | id=9 (profile 연결) | 생성 응답과 일치 + `product`/`freshness_profile` 채워짐 | ✅ |

## 변경 파일 목록

| 파일 | 내용 |
|------|------|
| `app/domains/ingredients/repository.py` | `get_food_by_id`, `create` 구현 |
| `app/domains/ingredients/service.py` | `create_ingredient`, `_resolve_expiration`, 3개 422 에러 클래스 |
| `shared/01_STATUS_BOARD.md` | BE-4 → ✅ |
| `dev_docs/.../260830dev_history/2260830_dev_history_02.md` | 본 기록 |

## 참고 — 스키마 갭에 대한 판단 근거

`13_be_create_api.md`가 요구하는 "제조일→포장일→구매일→수령일→등록일" 5단계
우선순위는 BE-1에서 이미 확정된 `ingredients` 테이블 컬럼(구매일까지만)으로는
그대로 구현할 수 없었다. 제조일/포장일/수령일 컬럼을 새로 추가하는 건 BE-1
정본화 범위를 다시 여는 일이라 BE-4에서 독단적으로 하지 않고, 현재 스키마
안에서 규칙의 취지(제조일 등 기준일이 불확실하면 확정하지 않는다)를 최대한
살리는 근사치로 구현했다. 실제 제조일 단위 정밀도가 필요해지면 별도 논의 후
스키마 확장이 필요하다.

## 체크포인트 (backend/13_be_create_api.md 기준)

- [x] 직접입력 등록 성공(product 없이)
- [x] default 값이 노션대로 (`expiration_source=USER_INPUT`, 확정 가능하면 `CONFIRMED`)
- [x] ESTIMATED 분기 동작
- [x] 검증 실패 422 + 필드별 details
- [x] 응답이 상세 스키마와 동일 필드 구성

## 다음

**BE-5**: 대시보드 집계 API (`GET /ingredients/summary`) — total/냉장/냉동 카운트,
임박(D-day) 기준 상수 정의, `expiring_items` top N.
