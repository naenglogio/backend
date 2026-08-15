# Jaeseung Dev Docs (NaengLog · 재성 담당)

재성 담당 4기능(상세/등록/카메라 인식/메인 3D 냉장고) 개발 문서.

## 폴더
- `backend/`  — 백엔드 테스크 문서 (BE-1~7)
- `frontend/` — 프론트 테스크 문서 (FE-0~6)
- `shared/`   — 프론트·백엔드 공유 (API 계약서, 진행 현황 보드)

## 각 레포에 넣는 법
- **백엔드 레포**: `backend/` + `shared/` 를 넣는다.
- **프론트 레포**: `frontend/` + `shared/` 를 넣는다.
- `shared/`는 **양쪽 레포에 모두** 들어가야 서로 상태를 인지할 수 있다.

## AI에게 시키는 법
해당 테스크 문서 + `shared/00_API_CONTRACT.md` + `shared/01_STATUS_BOARD.md`를 함께 읽힌다.
예) 백엔드 상세 API → `backend/12_be_list_detail_api.md` + shared 2개.

## 진행 원칙
- 정본 = 노션 ERD (storage_type = int).
- 프론트 타입은 이미 정의됨(별도 `naenglog_types`). 새로 만들지 말고 가져다 쓴다.
- 테스크 완료 시 `shared/01_STATUS_BOARD.md`의 상태를 ✅로 갱신.
