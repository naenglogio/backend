# 2026-08-16 개발 기록 — BE-2 #01 (schema 계약)

- 브랜치: `feat/ingredients`
- 테스크: BE-2 (ingredients 도메인 뼈대) — **1/N 슬라이스**
- 기준 문서: `backend/11_be_domain_skeleton.md`, `shared/00_API_CONTRACT.md`

## 분할 계획 (BE-2)

BE-2 전체를 한 번에 하지 않고 아래 순서로 나눈다.

| # | 슬라이스 | 산출물 | 상태 |
|---|----------|--------|:----:|
| 01 | API 계약 스키마 | `schema.py` | ✅ |
| 02 | repository 뼈대 | `repository.py` | ✅ (`_02.md`) |
| 03 | service 뼈대 | `service.py` | ✅ (`_03.md`) |
| 04 | router 뼈대 + 등록 | `router.py`, `api/router.py` | ✅ (`_04.md`) |

> 실제 엔드포인트 로직(목록/상세/등록/집계/인식)은 BE-3~7에서 채운다.
> 이번 슬라이스는 **Pydantic 요청·응답 계약만** 만든다.

## 목적

프론트 FE-1(`ingredientApi.ts`)이 기대하는 타입과 백엔드 응답 형태를 먼저 코드로 고정한다.
이후 repository/service/router가 이 스키마를 import해서 구현한다.

## 한 일

### `app/domains/ingredients/schema.py` 신규

계약서 엔드포인트별 스키마:

| 스키마 | 대응 API | 비고 |
|--------|----------|------|
| `Ingredient` | 목록 아이템 / 등록 응답 | `storage_type` = int 0\|1 |
| `IngredientCreateRequest` | `POST /ingredients` | quantity > 0, name 필수 |
| `IngredientDetailResponse` | `GET /ingredients/{id}` | Ingredient + product + freshness_profile |
| `ProductRead` | 상세 nested | 직접 입력이면 null |
| `ProductFreshnessProfileRead` | 상세 nested | 프로필 `storage_type`은 문자열 enum(유지) |
| `CameraRecognizeResponse` / `RecognitionCandidate` | `POST /recognitions` | confidence 0~1 |
| `IngredientSummaryResponse` / `ExpiringItem` | `GET /summary` | 대시보드 집계 |

공통:
- `from_attributes=True`로 ORM → 응답 변환 가능
- date/datetime은 JSON에서 `YYYY-MM-DD` / ISO로 직렬화
- enum은 기존 도메인 enum 재사용 (`ExpirationSource`, `ExpirationStatus`, `DeletionReason`, `ProductSource`)

## 아직 안 한 것

- `repository.py` / `service.py` / `router.py` 없음
- `app/api/router.py`에 ingredients 미등록 → Swagger에 ingredients API 아직 없음
- STATUS_BOARD BE-2는 전체 뼈대 완료 시에만 ✅ (지금은 유지 ⬜)

## 변경 파일

| 파일 | 내용 |
|------|------|
| `app/domains/ingredients/schema.py` | 신규 — API 계약 스키마 |
| `dev_docs/.../2260816_dev_history_01.md` | 본 기록 |

## 다음

BE-2 #02: `repository.py` 뼈대 (ORM 질의 자리만, 실제 쿼리는 BE-3~에서 채움)
