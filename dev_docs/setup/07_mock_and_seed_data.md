# 7단계 — Mock·Seed 데이터 기반 구축

## 목표

OCR/정제 파이프라인과 실제 운영 데이터가 준비되기 전에도 팀원 기능을 독립적으로 개발할 수 있게 한다.

## 데이터 구분

| 종류 | 목적 | 저장 위치 |
|---|---|---|
| Fixture | 테스트마다 재현되는 최소 데이터 | `tests/fixtures/` |
| Seed | 로컬 화면/API 개발용 샘플 | `scripts/` 또는 `app/db/seed/` |
| Mock contract | 외부 파이프라인 결과 형식 고정 | `dev_docs/contracts/` 또는 기존 contracts 위치 |

## Seed 최소 구성

- 사용자 3명
- 사용자별 device 1개 이상
- 표준 category/food 여러 건
- 컬리N마트 기반 product 여러 건
- 냉장·냉동 freshness profile
- 소비기한 임박/여유/경과 ingredient
- `CONSUMED`, `DISCARDED`, `WRONG_ENTRY` soft-deleted ingredient
- 읽음/안읽음 notification

## 데이터 파이프라인 계약

최종 적재 입력은 정제 완료 결과만 포함한다. 예시 필드는 다음과 같다.

```json
{
  "external_product_id": "5047857",
  "product_name": "예시 상품",
  "food_name": "예시 식품",
  "storage_type": "REFRIGERATED",
  "expiration_value": 7,
  "expiration_unit": "DAY",
  "expiration_basis": "AFTER_RECEIPT",
  "source": "INTEGRATED",
  "confidence": 0.91,
  "review_status": "APPROVED"
}
```

실제 계약이 별도 문서로 확정되면 그 문서를 우선한다. 원문 OCR JSON과 팀원별 CSV는 백엔드 운영 DB seed에 복사하지 않는다.

## 구현 작업

1. 여러 번 실행해도 중복 생성되지 않는 idempotent seed command를 만든다.
2. 고정된 테스트 값과 로컬 개발 값을 구분한다.
3. production 환경에서는 seed 실행을 차단한다.
4. 실제 파이프라인 adapter가 들어올 위치와 Mock adapter interface를 정의한다.
5. seed 초기화가 필요하면 명시적 옵션을 받고 데이터 삭제 범위를 제한한다.

## 검증

```bash
docker compose run --rm api alembic upgrade head
docker compose run --rm api python -m app.db.seed
docker compose run --rm api python -m app.db.seed
```

두 번째 실행 뒤 row 수가 불필요하게 증가하지 않아야 한다.

## 완료 조건

- 세 팀원이 실제 파이프라인 없이 기능을 개발할 수 있다.
- seed가 production에서 실행되지 않는다.
- 실제 데이터 전환 시 Service 계약을 바꿀 필요가 없다.

## AI 지시문

```text
실데이터가 아직 없다는 전제로 로컬 Seed, 테스트 Fixture, 파이프라인 Mock 계약을 만들어.
Seed는 idempotent하고 production에서 안전하게 차단되어야 해.
원문 OCR JSON이나 중간 CSV 전체를 운영 DB에 넣지 말고 최종 정제 필드만 사용해.
```
