#!/usr/bin/env python3
"""BE-8 문서 경로 진입점. 실제 로직은 `python -m app.batch.freshness_data_import`와 동일하다.

사용:
    python scripts/import_gold_bundle.py --bundle-dir /path/to/backend/export/<dataset_version>

bundle-dir은 crowling_ocr_parser의 `apps/normalizer/src/backend_publish`가 만든
export bundle 디렉터리(manifest.json, freshness_profiles.parquet, lineage.jsonl,
quality_summary.json)를 가리켜야 한다.

정본: dev_docs/Jaeseung_dev_docs/backend/17_be_gold_bundle_import.md
"""

from __future__ import annotations

import sys
from pathlib import Path

# 레포 루트에서 실행해도 `app` 패키지를 찾게 한다.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.batch.freshness_data_import import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
