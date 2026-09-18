# BE-7. 스캔 인식 API (사진/바코드/영수증 · fake adapter)

## 선행
BE-2 완료. (후보 food_id 매칭 품질을 위해 BE-6 seed 권장)

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (4. 카메라/바코드/영수증 인식)
- `dev_docs/mock_data_policy.md`

## 지시
```
POST /api/v1/ingredients/recognitions   (multipart)
fields: image (필수), mode=photo|barcode|receipt (기본 photo)
```
- 이미지 없거나 바이트가 비면 400.
- **실제 추론/OCR/바코드 디코딩은 하지 않는다.**
  `RecognizerPort` 인터페이스를 두고 모드별 **fake adapter**를 주입한다.
  `if mock_mode:` 분기 금지 — 실모델 교체 시 router/service 계약이 바뀌지 않아야 한다.
- 응답은 세 모드 모두 `CameraRecognizeResponse` = `{ candidates: RecognitionCandidate[] }`
  - `RecognitionCandidate`: `{ food_id(null 가능), name, category(null 가능), confidence }`
  - confidence 내림차순.
  - photo: 후보 3~5개 / barcode: 보통 1건 / receipt: 라인별 여러 건.
- 후보의 food_id는 seed의 foods와 매칭되게(등록 프리필에 바로 쓰이도록).
- 표시 name은 목업 정책대로 `[MOCK]` 접두어.

## 체크포인트
- [ ] 인식 로직이 인터페이스로 분리됨(실모델 교체 시 계약 불변)
- [ ] mode=photo|barcode|receipt 분기
- [ ] 이미지 없음/빈 파일 에러 처리
- [ ] photo 후보 3~5개, confidence 내림차순
- [ ] 응답이 등록 프리필(food_id/name/category)로 바로 쓰임

## 완료 후
`../shared/01_STATUS_BOARD.md`의 BE-7 → ✅.
프론트에 알릴 것: **스캔 화면(FE-4) 사진/바코드/영수증 실연동 가능**해짐.
