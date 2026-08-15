# BE-8. Gold bundle import (데이터 파이프라인 → Backend DB)

> 데이터 파이프라인(foodinfo_OCR)이 만든 **Gold freshness bundle**을 읽어 검증하고, `products` / `product_freshness_profiles` 테이블에 idempotent하게 upsert한다.
> 파이프라인은 파일(bundle)을 만들고, **백엔드가 그 파일을 먹어 DB에 넣는다.** 파이프라인이 DB에 직접 쓰지 않는다.

## 선행
- BE-1~2(도메인 계층) 완료.
- products / freshness 도메인 model 존재(확인됨). Service/Repository는 이 테스크에서 필요한 만큼 구현.

## 함께 읽을 문서
- 파이프라인 `dev_order/data_platform/10_gold_backend_publish.md` (**bundle 규격·전달 계약 — 정본**)
- 파이프라인 `contracts/gold_freshness.schema.json` (레코드 계약)
- 백엔드 `app/domains/freshness/model.py`, `app/domains/products/model.py`, `enums.py`
- 백엔드 계층 규칙(users 도메인 패턴): Router/Service/Repository 분리

## 입력: Gold bundle (파이프라인 산출물)
```
freshness_profiles.parquet   ← 공식 데이터
freshness_profiles.csv       ← 확인용(정본 아님)
manifest.json                ← dataset_version, schema_version, rule_version, checksums, row_count
quality_summary.json         ← 상태별 건수
```
경로: 초기엔 로컬/공유 경로 또는 클라우드 스토리지(S3/GCS)에서 접근. **API 방식은 쓰지 않는다**(10 문서: 초기 파일 import, API는 향후 ADR).

## Gold 레코드 → 백엔드 모델 매핑
gold_freshness 필드 → DB:
| Gold 필드 | Backend 반영 |
|-----------|--------------|
| external_product_id | `products.external_id` (source=KURLY_N_MART과 함께 상품 식별/생성) |
| food_mapping_key | `foods` 매칭 → `product_freshness_profiles.food_id` (매칭 실패 시 정책: skip+기록) |
| product_name | `products.name` |
| storage_type (REFRIGERATED/FROZEN/ROOM/UNKNOWN) | `product_freshness_profiles.storage_type`(백엔드 enum). **ROOM/UNKNOWN 정책**: 대응값 없으면 skip+기록 or 합의된 기본값 |
| expiration_value + expiration_unit | `expiration_days`(SmallInteger, **일수로 환산**: MONTH→*30, YEAR→*365 등 규칙 문서화) |
| expiration_basis | (참고) status 판정 근거 |
| selected_source | `expiration_source`(백엔드 enum: PRODUCT_DISCLOSURE/MFDS_REFERENCE 등으로 매핑) |
| review_status (APPROVED만 실림) | `expiration_status`: 확정 가능→CONFIRMED, 기준일 불명 등→ESTIMATED |
| dataset_version | import 이력/멱등 키 |

## import 절차 (10 문서의 5단계)
1. **검증**: manifest 읽어 schema_version·checksum·row_count 확인. bundle checksum 재계산 대조. 불일치 시 전체 중단(부분 적재 금지).
2. **중복 확인**: 이 dataset_version이 이미 import됐는지 확인. 됐으면 skip(멱등).
3. **staging**: 트랜잭션 안에서 처리. 실패 시 전체 롤백(부분 적재 없음).
4. **upsert**: **도메인 Service를 통해** products/product_freshness_profiles upsert.
   - products: `(source, external_id)` unique로 있으면 갱신/없으면 생성.
   - product_freshness_profiles: food_id(+product_id)로 기존 프로필 갱신/생성.
   - **Backend 내부 모델을 파이프라인에 노출하지 않는다**(계약으로만 연결).
5. **결과 기록**: import 이력(dataset_version, row_count, 적용/skip/실패 건수, 시각) 저장.

## 구현 위치
- `scripts/import_gold_bundle.py` (신규 — scripts 폴더 없으므로 생성). CLI 인자: `--bundle-dir`, `--dataset-version`(옵션, manifest 우선).
- 실제 upsert 로직은 `app/domains/freshness/service.py`, `app/domains/products/service.py`에 두고 스크립트는 오케스트레이션만.
- 계층 규칙 준수: 스크립트→Service→Repository→DB. 스크립트에 ORM 직접 질의 금지.

## 실행 방식 (배포 아님)
- 이 import는 **상시 서비스가 아니다.** 필요할 때 수동/온디맨드 실행.
- 파이프라인은 클라우드 상주 배포 대상이 아니며, bundle 파일만 백엔드가 접근 가능한 위치(로컬/S3/GCS)에 두고 이 스크립트를 돌린다.

## 체크포인트
- [ ] manifest/schema/checksum 검증, 불일치 시 중단
- [ ] 같은 dataset_version 재실행 시 중복 적재 없음(멱등)
- [ ] 실패 시 부분 적재 없음(트랜잭션 롤백)
- [ ] products `(source, external_id)` 기준 upsert
- [ ] expiration_value+unit → expiration_days 환산 규칙 문서화
- [ ] storage_type ROOM/UNKNOWN 처리 정책 반영(+매핑 근거 기록)
- [ ] review_status → CONFIRMED/ESTIMATED 매핑
- [ ] food 매칭 실패 레코드 skip+기록(조용히 버리지 않음)
- [ ] Service 경유 upsert(스크립트에 ORM 직접 질의 없음)
- [ ] import 이력 기록
- [ ] 서비스 범위 pytest 통과

## 완료 후
`../shared/01_STATUS_BOARD.md`에 BE-8 행 추가·✅.
파이프라인 쪽에 알릴 것: bundle 규격이 백엔드 import와 맞물림 확인(gold_freshness 계약 기준).

## 논의 필요 (팀)
- storage_type ROOM/UNKNOWN을 어떻게 할지(skip vs 기본 냉장).
- expiration 단위 환산 규칙(MONTH/YEAR → days) 합의.
- bundle 전달 경로(로컬 복사 vs S3/GCS 버킷).
