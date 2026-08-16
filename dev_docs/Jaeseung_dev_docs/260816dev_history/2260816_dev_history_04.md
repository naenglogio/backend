# 2026-08-16 개발 기록 — BE-2 #04 (router 등록)

- 브랜치: `feat/ingredients`
- 테스크: BE-2 (ingredients 도메인 뼈대) — **4/4 슬라이스 (BE-2 완료)**
- 기준 문서: `backend/11_be_domain_skeleton.md`
- 선행: #01 schema, #02 repository, #03 service 완료

## 목적

계약서 경로를 HTTP로 노출하고 Swagger(`/docs`)에 나타나게 한다.
Router는 입출력·인증·status code만 담당하고, 업무는 service에 위임한다.
지금은 service가 `NotImplementedError`라 호출 시 500이지만, 경로·스키마 계약은 고정된다.

## 한 일

### `app/domains/ingredients/router.py` 신규

| Method | Path | response | 구현 예정 |
|--------|------|----------|-----------|
| GET | `/api/v1/ingredients` | `Page[Ingredient]` | BE-3 |
| GET | `/api/v1/ingredients/summary` | `IngredientSummaryResponse` | BE-5 |
| POST | `/api/v1/ingredients/recognitions` | `CameraRecognizeResponse` (multipart) | BE-7 |
| GET | `/api/v1/ingredients/{id}` | `IngredientDetailResponse` | BE-3 |
| POST | `/api/v1/ingredients` | `Ingredient` 201 | BE-4 |

공통:
- `CurrentUserId` JWT 인증
- `DBSession`, `PageQuery`, `COMMON_ERROR_RESPONSES`
- ORM 없음 → service만 호출
- `/summary`, `/recognitions`를 `/{id}`보다 **먼저** 등록 (경로 충돌 방지)

### `app/api/router.py`

```python
api_router.include_router(ingredients_router, prefix="/ingredients", tags=["ingredients"])
```

### STATUS_BOARD

- BE-2 → ✅ (뼈대 완료. 실 로직은 BE-3~7)

## BE-2 진행 현황 (완료)

| # | 슬라이스 | 산출물 | 상태 |
|---|----------|--------|:----:|
| 01 | API 계약 스키마 | `schema.py` | ✅ |
| 02 | repository 뼈대 | `repository.py` | ✅ |
| 03 | service 뼈대 | `service.py` | ✅ |
| 04 | router 뼈대 + 등록 | `router.py`, `api/router.py` | ✅ |

## 변경 파일

| 파일 | 내용 |
|------|------|
| `app/domains/ingredients/router.py` | 신규 — HTTP 엔드포인트 |
| `app/api/router.py` | ingredients router 등록 |
| `pyproject.toml` | `python-multipart` 추가 (recognitions multipart) |
| `shared/01_STATUS_BOARD.md` | BE-2 ✅ |
| `dev_docs/.../2260816_dev_history_04.md` | 본 기록 |

## 참고

- 서버 기동 후 `http://localhost:8000/docs` 에서 ingredients 태그 확인 가능
- 엔드포인트 호출은 아직 501/500(`NotImplementedError`) — BE-3부터 채움

## 다음

**BE-3**: 목록/상세 API 실제 구현 (`list_ingredients`, `get_ingredient_detail` + repository 쿼리)
→ FE-2 상세·FE-6 3D 실연동 가능
