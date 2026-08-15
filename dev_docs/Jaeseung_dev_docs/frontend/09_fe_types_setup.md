# FE-0/1. 타입 레포 반영 + API 클라이언트

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md`
- 기존 `src/services/authApi.ts` (fetch 래퍼·ApiError 패턴)

## 지시
### FE-0. 타입 반영
- 이미 정의된 `types/models/`, `types/features/`, `utils/storage.ts`를 레포에 추가.
- `@/` 경로 별칭이 `tsconfig.json`/`vite.config.ts`에 있는지 확인, 없으면 추가(없으면 상대경로 사용).
- **기존 `types/index.ts`는 수정 금지.**

### FE-1. API 클라이언트
`src/services/ingredientApi.ts` 작성. `authApi.ts`의 fetch 래퍼·`ApiError`를 재사용.
- `listIngredients(params)` → `Page<Ingredient>`
- `getIngredient(id)` → `IngredientDetailResponse`
- `createIngredient(body: IngredientCreateRequest)` → `Ingredient`
- `getSummary()` → `IngredientSummaryResponse`
- `recognize(image: File)` → `CameraRecognizeResponse` (multipart)
- 반환·인자 타입은 전부 `types/features`/`types/models`에서 import.

## 체크포인트
- [ ] `npm run build` 통과 (기존 화면 안 깨짐)
- [ ] `types/index.ts` 무변경
- [ ] 5개 함수 타입 안전, `/api/v1` prefix
- [ ] 401/404/422 에러가 `ApiError`로 처리됨

## 완료 후
`../shared/01_STATUS_BOARD.md`의 FE-1 → ✅.
