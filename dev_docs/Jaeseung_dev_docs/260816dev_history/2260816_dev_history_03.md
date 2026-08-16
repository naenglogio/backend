# 2026-08-16 개발 기록 — BE-2 #03 (service 뼈대)

- 브랜치: `feat/ingredients`
- 테스크: BE-2 (ingredients 도메인 뼈대) — **3/N 슬라이스**
- 기준 문서: `backend/11_be_domain_skeleton.md`
- 선행: BE-2 #01 schema, #02 repository 완료

## 목적

Router가 호출하는 **유스케이스 함수**와 도메인 오류 타입을 먼저 고정한다.
이번 슬라이스는 시그니처·역할만 두고, 실제 업무 규칙은 BE-3~7에서 채운다.

## 한 일

### `app/domains/ingredients/service.py` 신규

**도메인 오류**
| 클래스 | code | status | 용도 |
|--------|------|--------|------|
| `IngredientNotFoundError` | `INGREDIENT_NOT_FOUND` | 404 | 없거나 남의 식재료 |

**유스케이스 (현재 NotImplementedError)**
| 함수 | 대응 API | 구현 예정 |
|------|----------|-----------|
| `list_ingredients` | `GET /ingredients` | BE-3 |
| `get_ingredient_detail` | `GET /ingredients/{id}` | BE-3 |
| `create_ingredient` | `POST /ingredients` | BE-4 |
| `get_ingredient_summary` | `GET /ingredients/summary` | BE-5 |
| `recognize_ingredient_image` | `POST /ingredients/recognitions` | BE-7 |

공통:
- 반환 타입은 #01 `schema.py` / 공통 `Page[T]` 사용
- ORM은 쓰지 않음 → 이후 repository만 호출
- `users`의 `AppError` 상속 패턴과 동일

## 아직 안 한 것

- `router.py` 없음 → HTTP 미노출
- STATUS_BOARD BE-2는 #04까지 끝나야 ✅

## BE-2 진행 현황

| # | 슬라이스 | 산출물 | 상태 |
|---|----------|--------|:----:|
| 01 | API 계약 스키마 | `schema.py` | ✅ |
| 02 | repository 뼈대 | `repository.py` | ✅ |
| 03 | service 뼈대 | `service.py` | ✅ |
| 04 | router 뼈대 + 등록 | `router.py`, `api/router.py` | ⬜ |

## 변경 파일

| 파일 | 내용 |
|------|------|
| `app/domains/ingredients/service.py` | 신규 — 유스케이스 뼈대 |
| `dev_docs/.../2260816_dev_history_03.md` | 본 기록 |

## 다음

BE-2 #04: `router.py` 엔드포인트 스텁 + `app/api/router.py`에 `/ingredients` 등록 (Swagger 노출)
