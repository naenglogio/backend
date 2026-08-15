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

## 4. 카메라 인식 — 카메라 화면
```
POST /api/v1/ingredients/recognitions   (multipart, image 필드)
```
- 이미지 없으면 에러.
- **MVP는 fake adapter**로 목업 후보 반환 (실제 추론 X). 인터페이스 뒤에 fake 주입 — 실모델 교체 시 계약 불변.
- 응답: `CameraRecognizeResponse` = `{ candidates: RecognitionCandidate[] }`

**RecognitionCandidate**
| 필드 | 타입 | 비고 |
|------|------|------|
| food_id | number\|null | 매칭 실패 시 null |
| name | string | |
| category | string\|null | 표시용 |
| confidence | number | 0~1, 내림차순 정렬 |

- 이 응답은 등록 화면 프리필(food_id, name, category)로 바로 사용.

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

---

## 상태 매핑 참고 (노션 5.4)
| 파이프라인 결과 | DB 적재 | 서비스 상태 |
|---|---|---|
| AUTO_CONFIRMED | O | CONFIRMED |
| ESTIMATED | O | ESTIMATED |
| REVIEW_REQUIRED / UNMATCHED / REJECTED | X | 적재 안 함 |
