"""로컬 개발용 seed 진입점.

    python -m app.db.seed          # idempotent 적재
    python -m app.db.seed --reset  # 이 스크립트가 만든 seed 데이터만 삭제 후 재적재

production에서는 실행을 차단한다.
"""

import argparse
import asyncio
import logging
import sys

from app.core.config import settings
from app.db.seed.runner import reset_seed_data, run_seed
from app.db.session import async_session_factory

logger = logging.getLogger(__name__)


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

    if settings.APP_ENV == "production":
        print("seed는 production 환경(APP_ENV=production)에서 실행할 수 없습니다.", file=sys.stderr)
        return 1

    asyncio.run(_run(reset=args.reset))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
