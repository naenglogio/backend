# 2026-08-15 개발 이력 (FE-0 타입 재배치)

## 배경 / 목적
- 문서(`09_fe_types_setup.md`, `00_README.md`) 기준 구조는 `types/models/`, `types/features/`, `utils/storage.ts`다.
- 레포에는 타입이 **평면(flat)** 으로 `src/types/`에 들어와 있었고, `src/types/index.ts`가 노션 모델 배럴로 **덮어써져** 선영·우희 화면이 깨질 수 있는 상태였다.
- FE-0을 **재배치 방식**으로 정리했다. 파일 내용은 그대로 두고 위치·배럴·alias·원복만 수행.

## 한 일

### 1. 폴더 재배치 (`git mv`)
모델 → `src/types/models/`
- `enums.ts`, `user.ts`, `userDevice.ts`, `category.ts`, `food.ts`
- `product.ts`, `productFreshnessProfile.ts`, `ingredient.ts`, `notification.ts`

기능 → `src/types/features/`
- `common.ts`, `ingredientDetail.ts`, `ingredientRegister.ts`
- `cameraRecognize.ts`, `fridge.ts`

유틸 → `src/utils/storage.ts`
- 기존 `src/types/storage.ts`를 이동 (storage_type int 0/1 ↔ 한글 라벨)

**이유:** feature/model 파일의 import(`./enums`, `../models/...`, `../types/models/enums`)가 이 구조를 전제로 작성되어 있었기 때문. 이동 후 import 경로를 점검했고 추가 수정 없이 일치했다.

### 2. 배럴 파일 생성
- `src/types/models/index.ts` — 9개 모델 + enums re-export
- `src/types/features/index.ts` — 5개 기능 re-export

**이유:** `@/types/models`, `@/types/features`로 한 곳에서 import하기 위한 공개 API.

### 3. 옛 `src/types/index.ts` 원복
선영·우희용 옛 스키마로 되돌림:
- `StorageType = 'fridge' | 'freezer'`
- `Ingredient` (`expiryDate`, `quantityGrams`, `storageType` 등)

**이유:** `IngredientCard`, `IngredientListPage`, `mocks/ingredients.ts` 등이 `from '../../types'`로 이 스키마를 사용한다. 노션 ERD 타입과 공존하되 **이 파일은 건드리지 않는 것**이 팀 규칙이다.

### 4. `@/` 경로 별칭 추가
- `tsconfig.app.json` / `tsconfig.json`: `"@/*": ["./src/*"]`
  - TypeScript 6에서 `baseUrl`이 deprecated라 **paths에 `./src` prefix만** 사용 (baseUrl 미사용)
- `vite.config.ts`: `resolve.alias['@'] = path.resolve(__dirname, 'src')`

**이유:** 문서·README 예시(`@/types/models` 등)와 실제 빌드/번들러 해석을 맞추기 위함.

### 5. 검증
- `yarn build` (`tsc -b && vite build`) → **성공 (에러 0)**
- 옛 index를 쓰는 Ingredient 목록 화면 타입이 빌드에 포함되어 통과 확인

## 하지 않은 일 (FE-0 범위 밖이었던 것)
- ~~FE-1 `ingredientApi.ts`~~ → 아래 FE-1 섹션에서 완료
- 타입 파일 **내용** 신규 작성/수정 없음 (이동·배럴·원복·alias만)

## 결과 체크 (FE-0)
| 항목 | 결과 |
|------|------|
| models/features/utils 구조 | ✅ |
| 내부 import 경로 | ✅ (추가 수정 불필요) |
| 옛 `types/index.ts` 원복 | ✅ |
| `@/` alias | ✅ |
| `yarn build` | ✅ |

---

# 2026-08-15 개발 이력 (FE-1 API 클라이언트)

## 배경 / 목적
- `09_fe_types_setup.md` FE-1: 계약서(`/api/v1`)에 맞는 식재료 API 클라이언트가 화면(FE-2~6)보다 먼저 필요하다.
- BE API는 아직 미완(STATUS_BOARD BE-3~7 ⬜)이지만, 클라이언트를 먼저 두면 화면은 목업/실서버 전환만 하면 된다.

## 한 일

### 1. `src/services/ingredientApi.ts` 작성
| 함수 | 메서드·경로 | 반환 |
|------|-------------|------|
| `listIngredients(params?)` | GET `/ingredients?...` | `Page<Ingredient>` |
| `getIngredient(id)` | GET `/ingredients/{id}` | `IngredientDetailResponse` |
| `createIngredient(body)` | POST `/ingredients` | `Ingredient` |
| `getSummary()` | GET `/ingredients/summary` | `IngredientSummaryResponse` |
| `recognize(image)` | POST `/ingredients/recognitions` (multipart `image`) | `CameraRecognizeResponse` |

**이유·설계 선택**
- `ApiError`는 `authApi.ts`에서 import 해 재사용 (401/404/422 동일 throw).
- 로그인 토큰은 `getAccessToken()` → `Authorization: Bearer` (계약서 “인증 토큰 사용”).
- 타입은 `@/types/models`, `@/types/features`만 사용. 옛 `types/index.ts` 무변경.
- `storage_type`은 int(0/1) 쿼리/바디 그대로 전송 (문자열 변환 없음).
- multipart는 `Content-Type`을 수동 설정하지 않음 (boundary는 브라우저가 붙임).

### 1-1. 로그인 영역과의 경계 (중요)
재성 FE-1 범위는 식재료 API 클라이언트뿐이다. **로그인 담당 코드를 바꾸지 않았다.**

| 대상 | 한 일 | 안 한 일 |
|------|--------|----------|
| `src/utils/authToken.ts` | `getAccessToken()` **호출만** | 파일 수정·토큰 키/저장 로직 변경 없음 |
| `src/services/authApi.ts` | `ApiError` **import만** | `login()`·`postJson`·파일 내용 수정 없음 |
| `LoginForm` / 토큰 저장 | — | 미수정 (로그인 성공 시 토큰 저장은 기존 담당 로직 그대로) |

즉 Bearer 헤더는 “이미 로그인 쪽에서 저장해 둔 토큰을 읽어 요청에 붙이는 것”이고, 토큰 발급·저장 구현을 새로 만든 것이 아니다. 이 내용은 `ingredientApi.ts` 파일 상단·import·`authHeaders` 주석에도 적어 두었다.

### 2. 문서 갱신
- `shared/01_STATUS_BOARD.md` FE-1 → ✅

### 3. 검증
- `yarn build` → **에러 0**
- `types/index.ts` 미수정

## 결과 체크 (FE-1 · 09 문서 체크포인트)
| 체크포인트 | 결과 |
|------------|------|
| build 통과 (기존 화면 안 깨짐) | ✅ `yarn build` |
| `types/index.ts` 무변경 | ✅ |
| 5개 함수 타입 안전, `/api/v1` prefix | ✅ |
| 401/404/422 → `ApiError` | ✅ `throwIfNotOk` |
