# 2026-09-18 개발 기록 — BE-6 (local seed)

- 브랜치: `feature/local-seed`
- 테스크: BE-6 (local seed)
- 기준 문서: `backend/15_be_seed.md`, `dev_docs/mock_data_policy.md`
- 선행: BE-1~5 완료 상태

## 목적

프론트가 목록/상세/3D/대시보드를 **실데이터로** 볼 수 있게 로컬 멱등 seed를
목업 정책에 맞춰 정리한다. 기존 `app/db/seed` 뼈대는 유지하고, BE-6 요구
(10건+, 시나리오 5종, MOCK 규칙, `scripts/seed_dev_data.py`, local/test 가드)를 채운다.

## 한 일

### 1. 목업 정책 문서 신설

레포에 없던 `dev_docs/mock_data_policy.md`를 추가했다(BE-6/00_README가 참조하던 파일).

- `[MOCK]` 접두어, `example.invalid` URL, `MOCK-*` external_id
- `APP_ENV=local|test`만 허용
- 시드 로그인: `seedpass123`

### 2. `app/db/seed/data.py` 전면 정리

| 항목 | 내용 |
|------|------|
| 유저 | `seed.userN@example.invalid` 3명, 비밀번호 `seedpass123` |
| foods | 12종 (카테고리 5) |
| products | `MOCK-*` 13건 — 그중 `MOCK-INACTIVE`는 비활성 시나리오 근사 |
| ingredients | 총 17건 / **user1 활성 12건** (냉장 8 + 냉동 4) |
| image_url | `https://example.invalid/mock/...` |

필수 시나리오 5종:

1. 냉장 확정 — `[MOCK] 우유 (냉장확정)` + profile CONFIRMED
2. 냉동 예상 — `[MOCK] 냉동만두 (냉동예상)` ESTIMATED
3. 프로필 없음(직접입력) — `[MOCK] 양파 (직접입력)` product_id null
4. 비활성 상품 — `MOCK-INACTIVE` 상품만 존재, ingredient/프로필 미연결
5. 소비기한 임박 — 고등어·요거트 (D-day ≤ 3)

> products 테이블에 `is_active` 컬럼이 없어, 비활성은 "어떤 활성 식재료에도
> 연결되지 않은 카탈로그 행"으로 근사했다. 스키마 확장이 필요하면 별도 논의.

### 3. `app/db/seed/runner.py`

- ingredient 멱등 키: `(user_id, name)` — 같은 food를 여러 건 넣을 수 있음
- 소비기한 기준일: KST (`_today_kst`)
- 유저 생성 시 `hash_password(SEED_PASSWORD)`. 이미 시드 비번이면 재해싱 안 함
- `--reset` 시 예전 `@naenglog.local` / `seed-prod-*` 식별자도 함께 정리

### 4. 진입점

- `scripts/seed_dev_data.py` — 문서가 요구한 경로 (내부적으로 `app.db.seed` 호출)
- `python -m app.db.seed` 동일
- `APP_ENV`가 `local`/`test`가 아니면 exit 1 (`production`·`development` 거부 확인)

## 검증

```
docker compose exec api python scripts/seed_dev_data.py --reset
docker compose exec api python scripts/seed_dev_data.py   # 멱등
```

| 체크 | 결과 |
|------|------|
| user1 활성 ingredients | 12건 ✅ |
| 2회 실행 후 products MOCK-* | 13건 유지 ✅ |
| MOCK-INACTIVE 연결 ingredient | 0건 ✅ |
| APP_ENV=production/development | 거부(exit 1) ✅ |
| seedpass123 로그인 해시 검증 | True ✅ |
| summary (user1) | total=12, 냉장=8, 냉동=4, expiring=3 ✅ |

## 변경 파일

| 파일 | 내용 |
|------|------|
| `dev_docs/mock_data_policy.md` | 목업 정책 (신규) |
| `app/db/seed/data.py` | MOCK 규칙 + 시나리오 5종 + 10건+ |
| `app/db/seed/runner.py` | 멱등 키·KST·비밀번호·legacy reset |
| `app/db/seed/__main__.py` | local/test 가드 |
| `scripts/seed_dev_data.py` | BE-6 문서 경로 진입점 |
| `shared/01_STATUS_BOARD.md` | BE-6 → ✅ |
| `260918dev_history/2260918_dev_history_01.md` | 본 기록 |

## 프론트에 알릴 것

- 로그인: `seed.user1@example.invalid` / `seedpass123`
- user1 활성 식재료 12건 (냉장/냉동/임박/만료 섞임) → 목록·3D·대시보드 확인 가능
- 실행: `docker compose exec api python scripts/seed_dev_data.py --reset`

## 다음

**BE-7**: 카메라/바코드/영수증 인식 API (fake adapter, mode 분기 예정)
