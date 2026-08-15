# BE-7. 카메라 인식 API (fake adapter)

## 선행
BE-2 완료.

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (4. 카메라 인식)
- `dev_docs/mock_data_policy.md`

## 지시
```
POST /api/v1/ingredients/recognitions   (multipart, image 필드)
```
- 이미지 없으면 에러.
- **실제 추론은 하지 않는다.** 인식 인터페이스(예: `RecognizerPort`)를 정의하고 그 뒤에 **fake adapter**를 주입해서 목업 후보를 반환한다. `if mock_mode:` 분기 금지 — 실제 모델로 교체할 때 router/service 계약이 바뀌지 않아야 한다.
- 응답: `CameraRecognizeResponse` = `{ candidates: RecognitionCandidate[] }`
  - `RecognitionCandidate`: `{ food_id(null 가능), name, category(null 가능), confidence }`
  - confidence 내림차순, 후보 3~5개.
- 후보의 food_id는 seed의 foods와 매칭되게(등록 프리필에 바로 쓰이도록).

## 체크포인트
- [ ] 인식 로직이 인터페이스로 분리됨(실모델 교체 시 계약 불변)
- [ ] 이미지 없음 에러 처리
- [ ] 후보 3~5개, confidence 내림차순
- [ ] 응답이 등록 프리필(food_id/name/category)로 바로 쓰임

## 완료 후
`../shared/01_STATUS_BOARD.md`의 BE-7 → ✅.
프론트에 알릴 것: **카메라 인식 화면(FE-4)이 실연동 가능**해짐.
