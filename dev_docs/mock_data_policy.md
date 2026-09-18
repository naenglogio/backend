# 목업·seed 데이터 정책

BE-6(`scripts/seed_dev_data.py`) 및 향후 fake adapter(BE-7)가 따르는 규칙.
실제 외부 상품/개인 데이터를 넣지 않는다.

## 식별 규칙

| 대상 | 규칙 | 예 |
|------|------|----|
| 화면 표시 이름 | `[MOCK]` 접두어 | `[MOCK] 우유` |
| URL | `example.invalid` 도메인만 | `https://example.invalid/mock/milk.jpg` |
| 상품 외부 ID (`products.external_id`) | `MOCK-*` | `MOCK-1001` |
| 시드 유저 이메일 | `@example.invalid` | `seed.user1@example.invalid` |

## 실행 규칙

- `APP_ENV`가 `local` 또는 `test`일 때만 실행. 그 외(development/production)는 거부.
- 반복 실행해도 행이 늘지 않게 **멱등**(natural key get-or-create).
- `--reset`은 이 스크립트가 만든 식별자 범위만 삭제 후 재적재.
- 코드에 `if mock_mode:` 분기를 두지 않는다. seed/fixture/fake adapter로만 격리.

## 로그인 (로컬 FE 연동)

시드 유저 비밀번호는 전원 동일: `seedpass123`  
(해시는 seed 적재 시 `hash_password`로 생성)
