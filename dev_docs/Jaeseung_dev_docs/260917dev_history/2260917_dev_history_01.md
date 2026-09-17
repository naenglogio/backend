# 2026-09-17 개발 기록 — BE-5 (대시보드 집계 API)

- 브랜치: `feat/summary-API`
- 테스크: BE-5 (집계 API)
- 기준 문서: `backend/14_be_summary_api.md`, `shared/00_API_CONTRACT.md` (5. 대시보드 집계)
- 선행: BE-3(목록/상세), BE-4(등록) 완료 상태에서 시작

## 목적

`GET /ingredients/summary`의 `NotImplementedError`를 실제 집계 로직으로 채운다.
라우터와 응답 스키마(`IngredientSummaryResponse` / `ExpiringItem`)는 BE-2에서 이미
만들어둔 것을 그대로 쓰고, repository·service만 구현했다.

## 한 일

### 1. `app/domains/ingredients/repository.py`

- `summarize_active_by_user` 구현. 쿼리는 2개로 나눴다.
  - 카운트: `COUNT(*) FILTER (WHERE ...)` 한 번으로 total / 냉장 / 냉동 / 임박을 동시에 센다.
    (profile 도메인 통계가 쓰는 것과 같은 패턴)
  - 임박 목록: 정렬과 `limit`이 필요하므로 별도 쿼리. `expiration_date asc, id asc`로
    급한 것부터 뽑고, 같은 날짜면 id로 순서를 고정해 재요청 시 결과가 흔들리지 않게 했다.
- 임박 판정 기준일(`today`)과 임계 일수는 **업무 규칙이라 service가 넘겨주고**, repository는
  받은 값으로 질의만 한다. 덕분에 기준일을 바꿔 끼우는 테스트가 쉬워진다.
- 반환은 BE-2에서 정해둔 시그니처대로 `dict`. service가 pydantic으로 검증·매핑한다.

### 2. `app/domains/ingredients/service.py`

- 임박 기준을 상수로 고정 (`14_be_summary_api.md`의 "상수로 정의하고 문서화" 요구사항):

  | 상수 | 값 | 의미 |
  |---|---|---|
  | `EXPIRING_WITHIN_DAYS` | 3 | `expiration_date <= 오늘+3` 이면 임박 |
  | `EXPIRING_ITEMS_TOP_N` | 5 | `expiring_items`에 노출할 최대 건수 |

  3일로 정한 근거: 프론트 `mock/home.ts`의 `DDay`가 0/1/3 리터럴을 쓰고 있고,
  `shared/02_DESIGN_SYSTEM.md`의 색 규칙이 "지남/오늘 = danger, 임박(N일 이내) = warning"이라
  FE 배지 기준과 맞추기 위함. FE와 값이 달라지면 화면 숫자와 배지가 어긋나므로 상수로 못박았다.

- `get_ingredient_summary` 구현: 상수와 기준일을 repository에 넘기고 결과를
  `IngredientSummaryResponse.model_validate(raw)`로 매핑.
- `today_in_service_tz()` 추가 (KST 기준 오늘):
  - 컨테이너 TZ가 UTC라 `date.today()`를 쓰면 **KST 00~09시에 하루 전 날짜**가 나온다.
    소비기한/D-day는 사용자가 화면에서 보는 날짜 기준이어야 하므로 KST로 계산한다.
  - 한국은 DST가 없어 `timezone(timedelta(hours=9))` 고정 오프셋으로 충분하다
    (slim 이미지에 tzdata가 없어도 동작).
  - **BE-4에서 쓰던 `date.today()`도 이 함수로 교체**했다. 같은 도메인 안에서 "오늘"의
    정의가 두 개인 게 더 위험하다고 판단. 등록 시 소비기한 계산 기준일도 같이 정확해진다.

### 3. 임박 판정 규칙 (문서화)

- 이미 **지난 항목도 임박에 포함**한다. `expiration_date <= 오늘+3` 조건이라 자연히 포함되며,
  대시보드에서 가장 먼저 조치해야 할 대상이기 때문에 의도한 동작이다.
- `expiration_date`가 null(직접입력·소비기한 미확정)이면 임박으로 세지 않지만 `total`에는 포함된다.
- `is_deleted=true`는 total·카운트·임박 전부에서 제외 (목록/상세와 가시성 일치).
- `expiring_count`는 **전체 임박 개수**이고 `expiring_items`는 top N이라, 임박이 5건을 넘으면
  `expiring_count > len(expiring_items)`가 정상이다. FE는 카드 개수 배지에 `expiring_count`를 써야 한다.

## 검증 (Docker, seed 데이터)

기준일 2026-09-17(KST). 기존 데이터 + 롤백하는 트랜잭션 안에서만 임시 행을 넣어 확인
(로컬 DB에 테스트 쓰레기 데이터를 남기지 않음).

| 시나리오 | 기대 | 결과 |
|---|---|---|
| user 3 (활성 4건, 전부 냉장) | total 4 / 냉장 4 / 냉동 0 | ✅ |
| soft delete 행 제외 (user 3의 id=4) | 어떤 카운트에도 안 잡힘 | ✅ |
| `expiration_date` null 행 (id=7) | total 포함, 임박 제외 | ✅ |
| 임박 정렬 | 08-11 → 08-31 → 09-10 순 | ✅ |
| 경계 D-3 (오늘+3) | 임박 **포함** | ✅ |
| 경계 D-4 (오늘+4) | 임박 **제외** | ✅ |
| 오늘 만료 (D-0) | 임박 포함 | ✅ |
| 냉동 행 추가 | `frozen_count` 증가, soft delete 냉동은 미포함 | ✅ |
| `top_n=2`로 호출 | items 2건으로 잘리고 `expiring_count`는 전체 유지 | ✅ |
| 데이터 없는 user 1 | 전부 0, `expiring_items: []` (에러 아님) | ✅ |
| 토큰 없음 / 잘못된 토큰 | 401 | ✅ |
| OpenAPI 스키마 | `total/refrigerated_count/frozen_count/expiring_count/expiring_items` + `ExpiringItem{id,name,storage_type(0\|1),expiration_date(nullable)}` — 계약서와 일치 | ✅ |

## 변경 파일 목록

| 파일 | 내용 |
|------|------|
| `app/domains/ingredients/repository.py` | `summarize_active_by_user` 구현 |
| `app/domains/ingredients/service.py` | `get_ingredient_summary`, 임박 상수 2개, `today_in_service_tz()` |
| `shared/01_STATUS_BOARD.md` | BE-5 → ✅ |
| `alembic/versions/63ff83cd4639_...py` | head 분기 정리용 merge revision (스키마 변경 없음) |
| `shared/00_API_CONTRACT.md` | 5항에 임박 기준(D-3, top 5) 명시 — FE와 값 공유 |
| `dev_docs/.../260917dev_history/2260917_dev_history_01.md` | 본 기록 |

`router.py`와 `schema.py`는 BE-2에서 만든 것으로 충분해 변경 없음.

## 체크포인트 (backend/14_be_summary_api.md 기준)

- [x] summary 응답이 계약서·프론트 타입과 일치
- [x] 냉장/냉동 카운트 정확
- [x] 임박 기준 명확·문서화 (D-3, top 5)
- [x] 집계 쿼리가 repository에 있고 router는 위임만

## 별건 — alembic head 분기 정리 (같은 브랜치에서 처리)

`92a7ff678da3`를 부모로 두 리비전이 나란히 생겨 head가 2개였다.

```
92a7ff678da3 (branchpoint)
  ├── a1b2c3d4e5f6  (BE-1 ingredients 정본화)   ← 로컬에 적용돼 있던 리비전
  └── 105c4a528885  (팀원의 password_resets)     ← 로컬 미적용
```

이 상태면 `alembic upgrade head`가 "Multiple head revisions"로 실패하고, 로컬에
`password_resets` 테이블이 없어 비밀번호 재설정 API가 동작하지 않았다.

**두 마이그레이션의 대상이 달라(기존 컬럼 변경 vs 새 테이블 생성) 실제 스키마 충돌은 없었다.**
히스토리만 갈라진 문제라 alembic 표준 방식인 merge revision으로 합쳤다.

```
alembic merge -m "merge ingredients and password_resets heads" 105c4a528885 a1b2c3d4e5f6
alembic upgrade head
```

- 생성 파일: `alembic/versions/63ff83cd4639_merge_ingredients_and_password_resets_.py`
  (`down_revision = ('105c4a528885', 'a1b2c3d4e5f6')`, upgrade/downgrade는 비어 있음 — 스키마 변경 없음)
- 적용 결과: `alembic_version` 단일 행 `63ff83cd4639`, `password_resets` 테이블 생성,
  `ingredients` 9행 그대로 유지. 적용 후 summary 응답도 동일함을 재확인.

**`down_revision`을 직접 고쳐 일렬로 만들지 않은 이유**: 두 리비전이 이미 `origin/main`에
올라가 있어 팀원 DB에는 둘 다 적용됐을 수 있다(그 경우 `alembic_version`에 2행). 공유된
리비전의 부모를 바꾸면 상대 쪽 적용 이력이 히스토리와 맞지 않게 된다.

**재발 방지**: 브랜치를 딸 때와 PR 올리기 전에 `alembic heads`가 한 줄인지 확인한다.

## 다음

**BE-6**: local seed (`scripts/seed_dev_data.py`) — 멱등 실행, `[MOCK]` 접두어,
필수 시나리오 5종, ingredients 10건+ 냉장/냉동/임박/만료 섞기.
FE-5(대시보드 실연동)는 이제 `getSummary()`로 진행 가능.
