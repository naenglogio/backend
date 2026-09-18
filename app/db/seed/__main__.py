"""로컬 개발용 seed 진입점.

    python -m app.db.seed          # idempotent 적재
    python -m app.db.seed --reset  # 이 스크립트가 만든 seed 데이터만 삭제 후 재적재

또는 문서 경로 별칭:
    python scripts/seed_dev_data.py [--reset]

APP_ENV=local|test 에서만 실행한다.
"""

import argparse
import asyncio
import logging
import sys

from app.core.config import settings
from app.db.seed.runner import reset_seed_data, run_seed
from app.db.session import async_session_factory

logger = logging.getLogger(__name__)

_ALLOWED_ENVS = frozenset({"local", "test"})


async def _run(*, reset: bool) -> None:
    async with async_session_factory() as session:
        if reset:
            await reset_seed_data(session)
        await run_seed(session)


def main() -> int:
    parser = argparse.ArgumentParser(description="로컬 개발용 seed 데이터를 적재한다.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="이 스크립트가 만든 seed 데이터만 먼저 삭제한 뒤 다시 적재한다.",
    )
    args = parser.parse_args()

    if settings.APP_ENV not in _ALLOWED_ENVS:
        print(
            f"seed는 APP_ENV=local|test 에서만 실행할 수 있습니다. (현재: {settings.APP_ENV})",
            file=sys.stderr,
        )
        return 1

    asyncio.run(_run(reset=args.reset))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
