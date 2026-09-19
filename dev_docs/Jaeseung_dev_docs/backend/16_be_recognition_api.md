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
- **사진/영수증**: 실비전·OCR은 아직 없고 DB 카탈로그 추정.
- **바코드**: 이미지에서 실제 디코딩(pyzbar) → `products.external_id` 매칭.
  - 디코딩 실패 → 빈 candidates (엉뚱한 상품 추정 금지)
  - 코드는 읽혔지만 미등록 → `food_id=null`, name=`미등록 상품 ({code})`
  - 매칭 성공 → 해당 상품/식품 후보
- `RecognizerPort` 뒤 adapter만 갈아끼우면 실모델로 교체 가능. `if mock_mode:` 금지.
- 후보 표시 name에 `[MOCK]` 접두어를 붙이지 않는다.

## 체크포인트
- [ ] 인식 로직이 인터페이스로 분리됨(실모델 교체 시 계약 불변)
- [ ] mode=photo|barcode|receipt 분기
- [ ] 이미지 없음/빈 파일 에러 처리
- [ ] photo 후보 3~5개, confidence 내림차순
- [ ] 응답이 등록 프리필(food_id/name/category)로 바로 쓰임

## 완료 후
`../shared/01_STATUS_BOARD.md`의 BE-7 → ✅.
프론트에 알릴 것: **스캔 화면(FE-4) 사진/바코드/영수증 실연동 가능**해짐.
