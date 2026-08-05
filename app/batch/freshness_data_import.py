"""정제 결과 적재 orchestration.

실행 순서와 개별 레코드 실패 시 재시도/건너뛰기만 담당한다. 실제 매핑·검증
규칙은 app.domains.freshness.service에 있다(이 모듈은 그 규칙을 모른다).

실제 파이프라인 adapter가 준비되면 FreshnessDataSource Protocol을 구현하는
클래스를 별도 모듈(예: app/batch/adapters/pipeline_source.py)로 만들어
run_import()에 넘기면 된다. 지금은 로컬 개발용 MockFreshnessDataSource만 있다.
"""

import asyncio
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from app.db.session import async_session_factory
from app.domains.freshness.contracts import RefinedFreshnessRecord
from app.domains.freshness.service import import_refined_record
from app.domains.products.enums import ProductSource

logger = logging.getLogger(__name__)


class FreshnessDataSource(Protocol):
    """정제 완료 레코드를 내주는 어댑터 계약. 실제 파이프라인/Mock 모두 이 형태를 만족한다."""

    def fetch_records(self) -> Iterable[RefinedFreshnessRecord]: ...


class MockFreshnessDataSource:
    """로컬 개발/테스트용 고정 예시 데이터. 실제 파이프라인 연동 전까지 사용한다."""

    def fetch_records(self) -> Iterable[RefinedFreshnessRecord]:
        return [
            RefinedFreshnessRecord(
                external_product_id="5047857",
                product_name="예시 우유 1L",
                food_name="우유",
                storage_type="REFRIGERATED",
                expiration_value=7,
                expiration_unit="DAY",
                expiration_basis="AFTER_RECEIPT",
                source="INTEGRATED",
                confidence=0.91,
                review_status="APPROVED",
                product_source=ProductSource.KURLY,
            ),
            RefinedFreshnessRecord(
                external_product_id="8812093",
                product_name="예시 냉동 만두",
                food_name="만두",
                storage_type="FROZEN",
                expiration_value=6,
                expiration_unit="MONTH",
                expiration_basis="AFTER_RECEIPT",
                source="INTEGRATED",
                confidence=0.62,
                review_status="PENDING",
                product_source=ProductSource.N_MART,
            ),
        ]


@dataclass(slots=True)
class ImportSummary:
    succeeded: int = 0
    failed: int = 0


async def run_import(source: FreshnessDataSource) -> ImportSummary:
    """레코드를 하나씩 저장한다. 레코드 하나가 실패해도 나머지는 계속 진행한다."""
    summary = ImportSummary()
    async with async_session_factory() as session:
        for record in source.fetch_records():
            try:
                await import_refined_record(session, record)
                await session.commit()
                summary.succeeded += 1
            except Exception:
                await session.rollback()
                logger.exception(
                    "Failed to import freshness record (external_product_id=%s)",
                    record.external_product_id,
                )
                summary.failed += 1
    return summary


def main() -> int:
    summary = asyncio.run(run_import(MockFreshnessDataSource()))
    logger.info(
        "Freshness import finished: succeeded=%s failed=%s", summary.succeeded, summary.failed
    )
    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
