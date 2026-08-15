# 프론트 개발 문서 (재성 담당)

> 이 폴더는 프론트 레포(`naenglogio/frontend`)에 넣는 개발 문서다.
> AI에게 작업 시킬 때는 **해당 테스크 MD + `../shared/00_API_CONTRACT.md` + `../shared/01_STATUS_BOARD.md`**를 함께 읽힌다.

## 대전제 (모든 테스크 공통)
- **정본 = 노션 ERD.** 필드·타입·enum은 노션 기준.
- **타입은 이미 정의됨**: `types/models/`(8개 테이블) + `types/features/`(담당 4기능) + `utils/storage.ts`. 새로 만들지 말고 **가져다 쓴다.**
- **기존 `types/index.ts`는 건드리지 않는다.** (선영·우희 화면이 씀 — 바꾸면 그쪽 빌드가 깨짐)
- storage_type은 int(0/1). 화면 표시는 `utils/storage.ts`의 `storageLabel`/`STORAGE_OPTIONS` 사용.
- API 호출은 기존 `services/authApi.ts`의 fetch 래퍼·`ApiError` 패턴 재사용, prefix `/api/v1`.
- **UI/디자인**: 기존 디자인 시스템을 따른다. `../shared/02_DESIGN_SYSTEM.md`의 Tailwind 토큰·기존 컴포넌트를 재사용하고, 임의 색·컴포넌트를 만들지 않는다. 각 화면 문서 하단의 'UI 명세'는 와이어프레임 기준이다.
- **선개발 전략**: 백엔드 API가 아직이면 계약서(`00_API_CONTRACT.md`) 기준으로 목업 응답으로 먼저 만들고, BE 완료 시 base URL만 실서버로 전환.

## 테스크 목록
| 파일 | 테스크 | 산출물 | 의존 BE |
|------|--------|--------|---------|
| 09_fe_types_setup.md | FE-0/1 | 타입 레포 반영 + API 클라이언트 | - |
| 20_fe_detail_page.md | FE-2 | 상세 화면 | BE-3 |
| 21_fe_create_page.md | FE-3 | 등록 화면 | BE-4 |
| 22_fe_recognize_page.md | FE-4 | 카메라 인식 화면 + 등록 연결 | BE-7 |
| 23_fe_dashboard_wire.md | FE-5 | MainPage 대시보드 실연동 | BE-5 |
| 24_fe_fridge3d.md | FE-6 | 메인 3D 냉장고 | BE-3 |

## 작업 완료 시
각 테스크 완료 후 `../shared/01_STATUS_BOARD.md`의 해당 FE 행을 ✅로 갱신한다.
