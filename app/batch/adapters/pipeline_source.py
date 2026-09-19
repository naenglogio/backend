"""app.batch.freshness_data_import.FreshnessDataSource의 실제 구현.

데이터 파이프라인(crowling_ocr_parser)이 파일로 넘겨준 Gold export bundle을 읽는다.
매핑·검증 규칙은 app.domains.freshness.gold_bundle에 있다 — 이 모듈은 경로를
받아 그 모듈을 호출하는 얇은 어댑터다.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from pathlib import Path

from app.domains.freshness.contracts import RefinedFreshnessRecord
from app.domains.freshness.gold_bundle import GoldBundleReadResult, load_gold_bundle

logger = logging.getLogger(__name__)


class GoldBundleFreshnessDataSource:
    """FreshnessDataSource Protocol 구현체 — Gold export bundle 디렉터리 하나를 읽는다."""

    def __init__(self, bundle_dir: Path) -> None:
        self.bundle_dir = bundle_dir
        self._result: GoldBundleReadResult | None = None

    def _load(self) -> GoldBundleReadResult:
        if self._result is None:
            self._result = load_gold_bundle(self.bundle_dir)
            logger.info(
                "Loaded gold bundle dataset_version=%s records=%s skipped=%s",
                self._result.dataset_version,
                len(self._result.records),
                len(self._result.skipped),
            )
        return self._result

    @property
    def dataset_version(self) -> str:
        return self._load().dataset_version

    @property
    def skipped_count(self) -> int:
        return len(self._load().skipped)

    def fetch_records(self) -> Iterable[RefinedFreshnessRecord]:
        return self._load().records
