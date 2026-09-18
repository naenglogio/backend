# API 계약서 (재성 담당 · SHARED)

> 프론트와 백엔드가 **함께 보는 단일 계약**이다. 백엔드는 이 응답을 만들고, 프론트는 이 응답을 받는다.
> 필드명·타입·enum은 **노션 ERD 정본**을 따른다. 여기와 코드가 다르면 코드를 고친다.
> 프론트 타입 정의(`types/models`, `types/features`)와 이 문서는 1:1로 일치해야 한다.

## 공통 규칙
- Base URL prefix: `/api/v1`
- 인증: 로그인 후 발급된 토큰 사용 (기존 `authApi.ts` 패턴)
- 목록 응답: `Page<T>` = `{ items: T[], page, size, total }`
- 오류 응답: `{ code: string, message: string, details?: unknown }`
- storage_type: **int (0=냉장, 1=냉동)**. 화면 표시만 프론트 `utils/storage.ts`로 한글 변환.
- 날짜: `date`는 `"YYYY-MM-DD"` 문자열, `datetime`은 ISO 문자열.

---

## 1. 상세 조회 — 상세 화면
```
GET /api/v1/ingredients/{id}
```
- 소유권 검증(본인 것만). 없거나 남의 것이면 404.
- 응답: `IngredientDetailResponse` = `Ingredient` + `product`(Product|null) + `freshness_profile`(ProductFreshnessProfile|null)
- 직접입력 식재료는 product/freshness_profile이 null.

**Ingredient 필드 (노션 ERD #7)**
| 필드 | 타입 | 비고 |
|------|------|------|
| id | number | |
| user_id | number | |
| food_id | number | |
| product_id | number\|null | 직접입력 시 null |
| freshness_profile_id | number\|null | 직접입력 시 null |
| name | string | |
| storage_type | number(int) | 0 냉장 / 1 냉동 |
| quantity | number | |
| unit | string\|null | |
| purchase_date | string\|null | date |
| expiration_date | string\|null | date |
| expiration_source | enum | USER_INPUT/PACKAGE_OCR/PRODUCT_DISCLOSURE/MFDS_REFERENCE |
| expiration_status | enum | CONFIRMED/ESTIMATED/REVIEW_REQUIRED |
| is_deleted | boolean | |
| deletion_reason | enum\|null | CONSUMED/DISCARDED/INCORRECT_ENTRY |
| image_url | string\|null | |
| memo | string\|null | |
| created_at | string | datetime |
| updated_at | string\|null | datetime |

---

## 2. 목록 조회 — 3D 냉장고 · 목록 공용
```
GET /api/v1/ingredients?storage_type={0|1}&expiration_status={..}&page={n}&size={n}
```
- 소유분·`is_deleted=false`만.
- 필터(storage_type, expiration_status)는 optional.
- 응답: `Page<Ingredient>`

---

## 3. 등록 — 등록 화면
```
POST /api/v1/ingredients
```
- 요청: `IngredientCreateRequest`

| 필드 | 타입 | 필수 | 비고 |
|------|------|:---:|------|
| food_id | number | O | |
| product_id | number\|null | | 직접입력 시 생략/null |
| freshness_profile_id | number\|null | | |
| name | string | O | |
| storage_type | number(int) | O | 0/1 |
| quantity | number | O | 양수 |
| unit | string\|null | | |
| purchase_date | string\|null | | date |
| expiration_date | string\|null | | date |
| expiration_source | enum | | 기본 USER_INPUT |
| image_url | string\|null | | |
| memo | string\|null | | |

- 검증 실패 시 422 (`{code,message,details}`)
- 기본값: `expiration_source=USER_INPUT`, `expiration_status=CONFIRMED`
- 소비기한 규칙: 기준일 불명 + "제조일로부터 N일"이면 `expiration_status=ESTIMATED`
- 응답: 생성된 `Ingredient`

---

## 4. 카메라/바코드/영수증 인식 — 스캔 화면
```
POST /api/v1/ingredients/recognitions   (multipart)
```
- 필드: `image`(필수), `mode`(선택, 기본 `photo`) — `photo` | `barcode` | `receipt`
- 이미지 없거나 비어 있으면 400.
- **MVP는 fake adapter**로 목업 후보 반환 (실제 추론/OCR/바코드 디코딩 X).
  인터페이스(`RecognizerPort`) 뒤에 모드별 fake 주입 — 실모델 교체 시 계약 불변.
  `if mock_mode:` 분기 금지.
- 응답: `CameraRecognizeResponse` = `{ candidates: RecognitionCandidate[] }` (세 모드 공통)

**RecognitionCandidate**
| 필드 | 타입 | 비고 |
|------|------|------|
| food_id | number\|null | foods 매칭 실패 시 null |
| name | string | `[MOCK]` 접두어(목업). 등록 프리필용 |
| category | string\|null | 표시용 |
| confidence | number | 0~1, 내림차순 정렬 |

**모드별 후보 규칙 (MVP)**
| mode | 후보 수 | 비고 |
|------|---------|------|
| photo | 3~5 | 식재료 사진 인식 |
| barcode | 1 (또는 매칭 실패 시 0) | 상품 1건 |
| receipt | 1~N | 영수증 라인별 후보 |

- 이 응답은 등록 화면 프리필(food_id, name, category)로 바로 사용.
- 후보 `food_id`는 seed foods와 매칭되게 둔다(BE-6).

---

## 5. 대시보드 집계 — MainPage
```
GET /api/v1/ingredients/summary
```
- 소유분·`is_deleted=false`만.
- 응답: `IngredientSummaryResponse`

| 필드 | 타입 | 비고 |
|------|------|------|
| total | number | 전체 보유 수 |
| refrigerated_count | number | storage_type=0 |
| frozen_count | number | storage_type=1 |
| expiring_count | number | 임박(D-day 이내) 수 |
| expiring_items | ExpiringItem[] | 임박 목록 top N |

**ExpiringItem**: `{ id, name, storage_type(int), expiration_date(string|null) }`

**임박 기준 (BE-5 확정)**
- `expiration_date <= 오늘(KST) + 3일` → 임박. **이미 지난 항목도 포함**한다.
- `expiration_date`가 null이면 임박에서 제외되지만 `total`에는 포함된다.
- `expiring_items`는 소비기한 오름차순 **최대 5건**. 임박이 5건을 넘으면
  `expiring_count > expiring_items.length`가 정상이므로, 개수 배지는 `expiring_count`를 쓴다.
- FE의 임박 배지 기준일수도 3일로 맞춰야 화면 숫자와 색이 어긋나지 않는다.

---

## 상태 매핑 참고 (노션 5.4)
| 파이프라인 결과 | DB 적재 | 서비스 상태 |
|---|---|---|
| AUTO_CONFIRMED | O | CONFIRMED |
| ESTIMATED | O | ESTIMATED |
| REVIEW_REQUIRED / UNMATCHED / REJECTED | X | 적재 안 함 |
