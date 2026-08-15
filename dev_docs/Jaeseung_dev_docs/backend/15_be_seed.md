# BE-6. local seed (목업 데이터)

## 선행
BE-1 완료 (모델 확정).

## 함께 읽을 문서
- `dev_docs/mock_data_policy.md` (반드시 준수)
- `../shared/00_API_CONTRACT.md`

## 지시
`scripts/seed_dev_data.py`를 목업 정책대로 작성하라.
- 규칙: `[MOCK]` 접두어, `example.invalid` URL, `original_product_id=MOCK-*`.
- `APP_ENV=local/test`에서만 실행되도록 가드. 반복 실행해도 중복 없게 **멱등**.
- 노션 8항 필수 시나리오 5종 포함: 냉장 확정 / 냉동 예상 / 프로필 없음(직접입력) / 비활성 상품 / 소비기한 임박.
- 3D 냉장고 배치 테스트를 위해 ingredients **10건 이상**, 냉장/냉동 골고루.
- 필드값은 정본 형식(storage_type int 0/1, enum 문자열 등).

## 체크포인트
- [ ] local/test에서만 실행되는가
- [ ] 2번 돌려도 중복 row 없는가(멱등)
- [ ] 필수 시나리오 5종 포함
- [ ] ingredients 10건+ (냉장/냉동/임박/만료 섞임)

## 완료 후
`../shared/01_STATUS_BOARD.md`의 BE-6 → ✅.
프론트에 알릴 것: **FE가 실데이터로 상세/목록/3D/대시보드 화면을 눈으로 확인 가능**해짐.
