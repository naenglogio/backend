#!/usr/bin/env python3
"""BE-6 문서 경로 진입점. 실제 로직은 `python -m app.db.seed` 와 동일하다.

사용:
    python scripts/seed_dev_data.py
    python scripts/seed_dev_data.py --reset

정책: `dev_docs/mock_data_policy.md`
"""

from __future__ import annotations

import sys
from pathlib import Path

# 레포 루트에서 실행해도 `app` 패키지를 찾게 한다.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.db.seed.__main__ import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
