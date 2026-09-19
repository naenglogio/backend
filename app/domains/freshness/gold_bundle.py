"""데이터 파이프라인(foodinfo_OCR/crowling_ocr_parser)이 만든 Gold export bundle을 읽는다.

계약 정본: 파이프라인 `contracts/backend_export_bundle.schema.json`,
`contracts/gold_freshness.schema.json`, `dev_order_docs/10_backend_publish.md`.
여기서는 그 계약을 백엔드 쪽에서 소비하는 부분만 다룬다 — 파이프라인 내부 모델은
import하지 않는다(파일 계약으로만 연결).
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from app.domains.freshness.contracts import RefinedFreshnessRecord
from app.domains.products.enums import ProductSource

logger = logging.getLogger(__name__)

_REQUIRED_MANIFEST_KEYS = (
    "schema_version",
    "dataset_version",
    "record_count",
    "freshness_profiles_checksum",
)

# 파이프라인 selected_source(KURLY/MFDS/MANUAL) 값은 그대로 RefinedFreshnessRecord.source에
# 실어 보낸다. 실제 enum 매핑은 app.domains.freshness.service._EXPIRATION_SOURCE_MAP이 담당한다.
_STORAGE_TYPE_MAP = {
    "REFRIGERATED": "REFRIGERATED",
    "FROZEN": "FROZEN",
    "ROOM": "ROOM_TEMPERATURE",
    # UNKNOWN은 backend StorageType에 대응값이 없다. 보수적으로 냉장 취급한다(팀 결정).
    "UNKNOWN": "REFRIGERATED",
}

# 파이프라인은 현재 컬리만 크롤링한다. product_source가 Gold 계약에 아직 없어
# 상수로 채운다 — 다른 마켓이 추가되면 계약에 필드를 추가해 대체해야 한다.
_PIPELINE_PRODUCT_SOURCE = ProductSource.KURLY


class GoldBundleValidationError(ValueError):
    """manifest·checksum·row-count 검증 실패. 전체 import를 중단시켜야 한다."""


@dataclass(frozen=True, slots=True)
class GoldRowSkipped:
    record_id: str
    reason: str


@dataclass(slots=True)
class GoldBundleReadResult:
    dataset_version: str
    records: list[RefinedFreshnessRecord]
    skipped: list[GoldRowSkipped]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(bundle_dir: Path) -> dict[str, Any]:
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.is_file():
        raise GoldBundleValidationError(f"bundle manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    missing = [key for key in _REQUIRED_MANIFEST_KEYS if key not in manifest]
    if missing:
        raise GoldBundleValidationError(f"manifest missing required keys: {missing}")
    if manifest["schema_version"] != "1.0.0":
        raise GoldBundleValidationError(
            f"unsupported backend_export_bundle schema_version: {manifest['schema_version']}"
        )
    return manifest


def verify_bundle_checksums(bundle_dir: Path, manifest: dict[str, Any]) -> None:
    """freshness_profiles.parquet checksum을 재계산해 manifest와 대조한다.

    gold_manifest_checksum은 원본 Gold bundle(파이프라인 내부 산출물)을 가리키므로
    이 export bundle만 갖고 있는 백엔드에서는 재계산할 수 없다 — lineage 참고용으로만
    manifest에 보존하고 별도 검증하지 않는다.
    """
    profiles_name = str(manifest.get("freshness_profiles_parquet") or "freshness_profiles.parquet")
    profiles_path = bundle_dir / profiles_name
    if not profiles_path.is_file():
        raise GoldBundleValidationError(f"bundle file missing: {profiles_path}")
    actual = _sha256_file(profiles_path)
    expected = manifest["freshness_profiles_checksum"]
    if actual != expected:
        raise GoldBundleValidationError(
            f"freshness_profiles checksum mismatch: expected={expected} actual={actual}"
        )


def read_gold_rows(bundle_dir: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    profiles_name = str(manifest.get("freshness_profiles_parquet") or "freshness_profiles.parquet")
    rows = pq.read_table(bundle_dir / profiles_name).to_pylist()
    expected_count = int(manifest["record_count"])
    if len(rows) != expected_count:
        raise GoldBundleValidationError(
            f"row count mismatch: manifest={expected_count} parquet={len(rows)}"
        )
    return rows


def map_gold_row(row: dict[str, Any]) -> RefinedFreshnessRecord | GoldRowSkipped:
    record_id = str(row.get("record_id") or row.get("external_product_id") or "unknown")

    review_status = str(row.get("review_status") or "")
    if review_status != "APPROVED":
        return GoldRowSkipped(record_id, f"NOT_APPROVED:{review_status}")

    expiration_value = row.get("expiration_value")
    expiration_unit = row.get("expiration_unit")
    if expiration_value is None or expiration_unit is None:
        return GoldRowSkipped(record_id, "MISSING_EXPIRATION")

    storage_raw = str(row.get("storage_type") or "").upper()
    storage_type = _STORAGE_TYPE_MAP.get(storage_raw)
    if storage_type is None:
        return GoldRowSkipped(record_id, f"UNSUPPORTED_STORAGE_TYPE:{storage_raw}")

    food_name = str(row.get("food_mapping_key") or "").strip()
    if not food_name:
        return GoldRowSkipped(record_id, "MISSING_FOOD_MAPPING_KEY")

    return RefinedFreshnessRecord(
        external_product_id=str(row.get("external_product_id") or ""),
        product_name=str(row.get("product_name") or ""),
        food_name=food_name,
        storage_type=storage_type,
        expiration_value=int(round(float(expiration_value))),
        expiration_unit=str(expiration_unit).upper(),
        expiration_basis=str(row.get("expiration_basis") or "UNKNOWN"),
        source=str(row.get("selected_source") or ""),
        confidence=float(row.get("confidence") or 0.0),
        review_status=review_status,
        product_source=_PIPELINE_PRODUCT_SOURCE,
    )


def load_gold_bundle(bundle_dir: Path) -> GoldBundleReadResult:
    """Gold export bundle 디렉터리를 검증하고 RefinedFreshnessRecord 목록으로 변환한다.

    manifest/checksum/row-count 불일치는 GoldBundleValidationError로 전체 중단시킨다.
    레코드 단위 문제(소비기한 누락 등)는 skip하고 사유를 기록한다 — 조용히 버리지 않는다.
    """
    manifest = read_manifest(bundle_dir)
    verify_bundle_checksums(bundle_dir, manifest)
    rows = read_gold_rows(bundle_dir, manifest)

    records: list[RefinedFreshnessRecord] = []
    skipped: list[GoldRowSkipped] = []
    for row in rows:
        mapped = map_gold_row(row)
        if isinstance(mapped, GoldRowSkipped):
            logger.warning(
                "Skipping gold record record_id=%s reason=%s", mapped.record_id, mapped.reason
            )
            skipped.append(mapped)
        else:
            records.append(mapped)

    return GoldBundleReadResult(
        dataset_version=str(manifest["dataset_version"]),
        records=records,
        skipped=skipped,
    )
