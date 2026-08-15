# 백엔드 개발 문서 (재성 담당)

> 이 폴더는 백엔드 레포(`naenglogio/backend`)에 넣는 개발 문서다.
> AI에게 작업 시킬 때는 **해당 테스크 MD + `../shared/00_API_CONTRACT.md` + `../shared/01_STATUS_BOARD.md`**를 함께 읽힌다.

## 대전제 (모든 테스크 공통)
- **정본 = 노션 ERD.** 필드·타입·enum은 노션 기준. 코드가 다르면 코드를 고친다.
- **계층 강제**: `Router → Service → Repository → Database`. router에서 ORM 직접 질의 금지. 기존 `users` 도메인 패턴을 그대로 따른다.
- **목업 정책** (`dev_docs/mock_data_policy.md`): `if mock_mode:` 금지, fixture/factory/`scripts/seed_dev_data.py`로만 격리. `[MOCK]` 접두어, `example.invalid` 도메인, `MOCK-*` id. seed는 `APP_ENV=local/test`에서만, 멱등.
- **소유권**: ingredients는 user_id 소유분만. 남의 것 접근 시 404/403 일관.
- **삭제는 논리삭제**: `is_deleted` + `deletion_reason`. 물리 삭제 금지.
- 공통 응답: `Page[T]`, 오류 `{code,message,details}`, prefix `/api/v1`.
- **프론트 계약 일치**: schema 필드는 `../shared/00_API_CONTRACT.md` 및 프론트 `types/features`와 1:1.

## 테스크 목록
| 파일 | 테스크 | 산출물 |
|------|--------|--------|
| 10_be_model_migration.md | BE-1 | ingredients 모델 정본화 + 마이그레이션 |
| 11_be_domain_skeleton.md | BE-2 | schema/repository/service/router 세트 |
| 12_be_list_detail_api.md | BE-3 | 목록/상세 조회 API |
| 13_be_create_api.md | BE-4 | 등록 API |
| 14_be_summary_api.md | BE-5 | 대시보드 집계 API |
| 15_be_seed.md | BE-6 | local seed |
| 16_be_recognition_api.md | BE-7 | 카메라 인식 API (fake adapter) |

## 작업 완료 시
각 테스크 완료 후 `../shared/01_STATUS_BOARD.md`의 해당 BE 행을 ✅로 갱신한다.
