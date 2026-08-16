# 2026-08-16 개발 기록 — BE-2 #02 (repository 뼈대)

- 브랜치: `feat/ingredients`
- 테스크: BE-2 (ingredients 도메인 뼈대) — **2/N 슬라이스**
- 기준 문서: `backend/11_be_domain_skeleton.md`
- 선행: BE-2 #01 (`schema.py`) 완료

## 목적

Router → Service → **Repository** → Database 계층에서 ORM 질의를 모을 자리를 만든다.
이번 슬라이스는 **메서드 시그니처·역할만** 정의하고, 실제 SQL은 BE-3~5에서 채운다.

## 한 일

### `app/domains/ingredients/repository.py` 신규

| 함수 | 용도 | 구현 예정 |
|------|------|-----------|
| `list_active_by_user` | 소유·활성 목록 + total (필터·페이지) | BE-3 |
| `get_owned_by_id` | 본인 단건 (없으면 None → 404) | BE-3 |
| `get_product_by_id` | 상세 nested product | BE-3 |
| `get_freshness_profile_by_id` | 상세 nested profile | BE-3 |
| `create` | 식재료 insert | BE-4 |
| `summarize_active_by_user` | 대시보드 집계 raw | BE-5 |

공통:
- `AsyncSession`만 받음
- 지금은 모두 `NotImplementedError("BE-N에서 구현")`
- 카메라 인식(BE-7)은 DB보다 fake adapter 성격이라 repository에 두지 않음

## 아직 안 한 것

- service / router 없음
- `api/router.py` ingredients 미등록
- STATUS_BOARD BE-2는 전체 뼈대 완료 시 ✅ (아직 ⬜)

## BE-2 진행 현황

| # | 슬라이스 | 산출물 | 상태 |
|---|----------|--------|:----:|
| 01 | API 계약 스키마 | `schema.py` | ✅ |
| 02 | repository 뼈대 | `repository.py` | ✅ |
| 03 | service 뼈대 | `service.py` | ⬜ |
| 04 | router 뼈대 + 등록 | `router.py`, `api/router.py` | ⬜ |

## 변경 파일

| 파일 | 내용 |
|------|------|
| `app/domains/ingredients/repository.py` | 신규 — DB 질의 뼈대 |
| `dev_docs/.../2260816_dev_history_02.md` | 본 기록 |

## 다음

BE-2 #03: `service.py` 뼈대 (업무 규칙·트랜잭션 자리, repository 호출만 위임)
