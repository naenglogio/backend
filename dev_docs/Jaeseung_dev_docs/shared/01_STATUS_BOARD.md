# 진행 현황 보드 (SHARED · 서로 인지용)

> 프론트/백엔드가 **상대가 지금 뭘 만들어놨는지** 확인하는 곳.
> 각 테스크 완료 시 담당자가 상태를 `⬜ 대기 → 🟡 진행 → ✅ 완료`로 갱신한다.
> AI에게 작업 시킬 때 이 파일을 먼저 읽혀서 "상대 준비 상태"를 인지시킨다.

## 의존 관계 요약

- 프론트 화면(상세/등록/집계)은 **백엔드 API가 완료돼야** 실연동된다.
  → API 미완이면 프론트는 계약서(`00_API_CONTRACT.md`) 기준으로 목업 응답으로 선개발 가능.
- 카메라 인식 화면(FE)은 인식 API(BE)에 의존.
- 3D 냉장고(FE)는 목록 API(BE)에 의존.

## 백엔드 상태

| ID   | 산출물                        | 엔드포인트/파일                | 상태 | 프론트가 알아야 할 것                    |
| ---- | ----------------------------- | ------------------------------ | :--: | ---------------------------------------- |
| BE-1 | ingredients 모델+마이그레이션 | model.py                       |  ⬜  | 스키마 확정 전까지 FE는 계약서 기준 목업 |
| BE-2 | 도메인 파일 세트              | schema/repo/service/router     |  ⬜  |                                          |
| BE-3 | 목록/상세 API                 | GET /ingredients, /{id}        |  ⬜  | 완료 시 상세·3D 화면 실연동 가능         |
| BE-4 | 등록 API                      | POST /ingredients              |  ⬜  | 완료 시 등록 화면 실연동 가능            |
| BE-5 | 집계 API                      | GET /ingredients/summary       |  ⬜  | 완료 시 대시보드 실연동 가능             |
| BE-6 | local seed                    | scripts/seed_dev_data.py       |  ⬜  | 완료 시 FE가 실데이터로 화면 확인        |
| BE-7 | 카메라 인식 API               | POST /ingredients/recognitions |  ⬜  | 완료 시 인식 화면 실연동 가능            |

## 프론트 상태

| ID   | 산출물           | 파일                         | 상태 | 백엔드가 알아야 할 것                    |
| ---- | ---------------- | ---------------------------- | :--: | ---------------------------------------- |
| FE-0 | 타입 정의        | types/models, types/features |  ✅  | 계약서와 1:1. BE schema는 이 타입에 맞춤 |
| FE-1 | API 클라이언트   | services/ingredientApi.ts    |  ⬜  | 계약서 경로/타입대로 호출                |
| FE-2 | 상세 화면        | pages/IngredientDetailPage   |  ⬜  | BE-3 필요                                |
| FE-3 | 등록 화면        | pages/IngredientCreatePage   |  ⬜  | BE-4 필요                                |
| FE-4 | 카메라 인식 화면 | pages/RecognizePage          |  ⬜  | BE-7 필요                                |
| FE-5 | 대시보드 실연동  | homeApi.ts, MainPage         |  ⬜  | BE-5 필요                                |
| FE-6 | 3D 냉장고        | MainPage 내 컴포넌트         |  ⬜  | BE-3 필요                                |

## 권장 순서 (의존성 최소 충돌)

1. FE-0 완료(✅) → BE-1 → BE-2 → BE-3/BE-4/BE-5 → BE-6
2. FE-1(클라이언트) → FE-2/FE-3(상세·등록) → FE-5(대시보드)
3. BE-7 → FE-4(카메라) → 인식→등록 연결
4. FE-6(3D) 마지막

> FE는 BE 완료를 기다리지 않고 계약서 기준으로 선개발 후, BE 완료 시 base URL만 실서버로 전환하는 방식 권장.
