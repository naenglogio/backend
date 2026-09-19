import hashlib
import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from app.domains.freshness import gold_bundle
from app.domains.freshness.gold_bundle import (
    GoldBundleValidationError,
    GoldRowSkipped,
    load_gold_bundle,
)
from app.domains.products.enums import ProductSource

_BASE_ROW: dict[str, Any] = {
    "record_id": "gold-1",
    "external_product_id": "5047857",
    "food_mapping_key": "우유",
    "product_name": "예시 우유 1L",
    "storage_type": "REFRIGERATED",
    "expiration_value": 7,
    "expiration_unit": "DAY",
    "expiration_basis": "AFTER_RECEIPT",
    "selected_source": "KURLY",
    "confidence": 0.91,
    "review_status": "APPROVED",
}


def _write_bundle(tmp_path: Path, rows: list[dict[str, Any]]) -> Path:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    profiles_path = bundle_dir / "freshness_profiles.parquet"
    table = pa.Table.from_pylist(rows) if rows else pa.table({k: [] for k in _BASE_ROW})
    pq.write_table(table, profiles_path)

    checksum = hashlib.sha256(profiles_path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": "1.0.0",
        "dataset_version": "20260901-jaeseong-001__KFIA-2026-08",
        "pair_id": "20260901-jaeseong-001__KFIA-2026-08",
        "kurly_batch_id": "20260901-jaeseong-001",
        "kfia_dataset_version": "KFIA-2026-08",
        "record_count": len(rows),
        "freshness_profiles_parquet": "freshness_profiles.parquet",
        "freshness_profiles_checksum": checksum,
        "code_version": "test",
        "rule_version": "backend_publish_v1.0.0",
        "created_at": "2026-09-01T00:00:00+09:00",
    }
    (bundle_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    return bundle_dir


def test_load_gold_bundle_maps_approved_row(tmp_path: Path) -> None:
    bundle_dir = _write_bundle(tmp_path, [_BASE_ROW])

    result = load_gold_bundle(bundle_dir)

    assert result.dataset_version == "20260901-jaeseong-001__KFIA-2026-08"
    assert result.skipped == []
    assert len(result.records) == 1
    record = result.records[0]
    assert record.external_product_id == "5047857"
    assert record.food_name == "우유"
    assert record.storage_type == "REFRIGERATED"
    assert record.expiration_value == 7
    assert record.source == "KURLY"
    assert record.product_source is ProductSource.KURLY


def test_load_gold_bundle_maps_room_and_unknown_storage(tmp_path: Path) -> None:
    room_row = {**_BASE_ROW, "record_id": "gold-room", "storage_type": "ROOM"}
    unknown_row = {**_BASE_ROW, "record_id": "gold-unknown", "storage_type": "UNKNOWN"}
    bundle_dir = _write_bundle(tmp_path, [room_row, unknown_row])

    result = load_gold_bundle(bundle_dir)

    storage_by_id = {r.external_product_id: r.storage_type for r in result.records}
    assert len(result.records) == 2
    assert all(value in {"ROOM_TEMPERATURE", "REFRIGERATED"} for value in storage_by_id.values())
    # ROOM -> ROOM_TEMPERATURE, UNKNOWN -> REFRIGERATED(팀 결정)
    room_record = next(r for r in result.records if r.storage_type == "ROOM_TEMPERATURE")
    unknown_record = next(r for r in result.records if r.storage_type == "REFRIGERATED")
    assert room_record is not None
    assert unknown_record is not None


def test_load_gold_bundle_skips_missing_expiration(tmp_path: Path) -> None:
    row = {**_BASE_ROW, "expiration_value": None, "expiration_unit": None}
    bundle_dir = _write_bundle(tmp_path, [row])

    result = load_gold_bundle(bundle_dir)

    assert result.records == []
    assert len(result.skipped) == 1
    assert isinstance(result.skipped[0], GoldRowSkipped)
    assert result.skipped[0].reason == "MISSING_EXPIRATION"


def test_load_gold_bundle_skips_non_approved(tmp_path: Path) -> None:
    row = {**_BASE_ROW, "review_status": "REVIEW_REQUIRED"}
    bundle_dir = _write_bundle(tmp_path, [row])

    result = load_gold_bundle(bundle_dir)

    assert result.records == []
    assert result.skipped[0].reason == "NOT_APPROVED:REVIEW_REQUIRED"


def test_verify_bundle_checksums_raises_on_mismatch(tmp_path: Path) -> None:
    bundle_dir = _write_bundle(tmp_path, [_BASE_ROW])
    manifest_path = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["freshness_profiles_checksum"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(GoldBundleValidationError, match="checksum mismatch"):
        load_gold_bundle(bundle_dir)


def test_read_gold_rows_raises_on_row_count_mismatch(tmp_path: Path) -> None:
    bundle_dir = _write_bundle(tmp_path, [_BASE_ROW])
    manifest_path = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["record_count"] = 2
    manifest["freshness_profiles_checksum"] = hashlib.sha256(
        (bundle_dir / "freshness_profiles.parquet").read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(GoldBundleValidationError, match="row count mismatch"):
        load_gold_bundle(bundle_dir)


def test_read_manifest_rejects_missing_required_keys(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    (bundle_dir / "manifest.json").write_text(
        json.dumps({"schema_version": "1.0.0"}), encoding="utf-8"
    )

    with pytest.raises(GoldBundleValidationError, match="missing required keys"):
        gold_bundle.read_manifest(bundle_dir)
