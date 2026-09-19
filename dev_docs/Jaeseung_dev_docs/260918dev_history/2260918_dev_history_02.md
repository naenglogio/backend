# 2026-09-18 개발 기록 — BE-7 (스캔 인식 API)

- 브랜치: `feature/recognition-API`
- 테스크: BE-7 (사진/바코드/영수증 인식 · fake adapter)
- 기준 문서: `backend/16_be_recognition_api.md`, `shared/00_API_CONTRACT.md` §4
- 선행: BE-2 뼈대, BE-6 seed(후보 food_id 매칭)

## 목적

`POST /ingredients/recognitions`의 `NotImplementedError`를 채우고,
FE-4 스캔 탭(사진/바코드/영수증)이 같은 응답 스키마로 실연동되게 한다.
실제 ML/OCR/바코드 디코딩은 하지 않고 **RecognizerPort + fake adapter**로 격리한다.

## 한 일

### 1. 계약·문서

- `00_API_CONTRACT.md` §4: `mode=photo|barcode|receipt` 추가, 모드별 후보 규칙 명시
- `16_be_recognition_api.md`: 3모드 범위로 확장
- `22_fe_recognize_page.md`: placeholder 문구 제거, mode 실연동 전제 반영

### 2. 인식 패키지 `app/domains/ingredients/recognition/`

| 파일 | 역할 |
|------|------|
| `port.py` | `RecognitionMode`, `RecognitionHint`, `RecognizerPort` |
| `fake.py` | `FakePhotoRecognizer`(5) / `FakeBarcodeRecognizer`(1) / `FakeReceiptRecognizer`(4) |
| `__init__.py` | export + `build_fake_recognizer_registry()` |

`if mock_mode:` 분기 없음. 실모델 교체 시 레지스트리만 갈아끼우면 router/service 계약 유지.

### 3. service / repository / router

- `recognize_ingredient_image`: 빈 이미지 → `IMAGE_MISSING` 400
- hint의 `food_name`으로 foods+categories 조회 → `food_id`/`category` 채움
- 표시 name은 foods 이름 그대로(예: `우유`). `[MOCK]` 접두어 없음
- confidence 내림차순 정렬
- router: multipart `image` + form `mode`(기본 `photo`)

### 4. repository

- `list_foods_with_categories_by_names`: 인식 후보 매칭용

## 검증

| 시나리오 | 기대 | 결과 |
|---|---|---|
| mode=photo | 200, 후보 5, food_id 전부 | ✅ |
| mode=barcode | 200, 후보 1 | ✅ |
| mode=receipt | 200, 후보 4 | ✅ |
| mode 생략 | photo와 동일(5건) | ✅ |
| 빈 이미지 | 400 `IMAGE_MISSING` | ✅ |
| image 필드 누락 | 422 | ✅ |
| 토큰 없음 | 401 | ✅ |
| seed 미존재 food면 food_id null 가능 | (현재 fake는 전부 seed foods) | ✅ |

## 변경 파일

| 파일 | 내용 |
|------|------|
| `app/domains/ingredients/recognition/*` | Port + fake adapters |
| `app/domains/ingredients/service.py` | 인식 로직·에러 클래스 |
| `app/domains/ingredients/repository.py` | foods 매칭 조회 |
| `app/domains/ingredients/router.py` | mode Form 필드 |
| `shared/00_API_CONTRACT.md` | §4 확장 |
| `backend/16_be_recognition_api.md` | BE-7 지시 갱신 |
| `frontend/22_fe_recognize_page.md` | FE 연동 안내 |
| `shared/01_STATUS_BOARD.md` | BE-7 → ✅ |
| `260918dev_history/2260918_dev_history_02.md` | 본 기록 |

## 프론트에 알릴 것

```
POST /api/v1/ingredients/recognitions
multipart: image, mode=photo|barcode|receipt
```

- 응답은 세 모드 모두 `{ candidates: [{ food_id, name, category, confidence }] }`
- seed 적재 후 food_id가 채워짐 → 등록 프리필 바로 가능
- MVP는 내부 fake adapter지만, 후보 name에는 `[MOCK]`을 붙이지 않음

## 후속 (2026-09-19) — 바코드 실디코딩

문제: 바코드 모드가 이미지를 읽지 않고 카탈로그에서 임의 상품을 골라
과자 사진인데 `컬리 즉석밥` 97%가 나왔다.

조치:
- `pyzbar` + `libzbar0` + Pillow로 바코드 디코딩
- 매칭: `products.external_id == 디코딩값`
- 실패 시 빈 목록 / 미등록 시 `food_id=null`
- 시드에 EAN `8809841063326` → `스낵 과자` 추가 (화면 테스트용)

검증: 생성 EAN 이미지 → `스낵 과자` 매칭, 비이미지 → `[]`, 미등록 EAN → 미등록 후보.

## 다음

재성 담당 BE-1~7 트랙은 여기까지. 여력 있으면 BE-8(gold bundle import) 또는
실모델 Recognizer 교체.
