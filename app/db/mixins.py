from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class IDMixin:
    """모든 MVP 테이블이 동일한 정수 PK 전략을 쓰므로 공통 mixin으로 중복을 줄인다."""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)


class TimestampMixin:
    """생성/수정 시각 공통 컬럼.

    DB 컬럼 타입을 timestamptz(DateTime(timezone=True))로 두면 PostgreSQL이 항상
    UTC 기준 시점(instant)을 저장하므로, 저장은 DB(UTC)에 맡기고 표시용 timezone
    변환은 API 계층 책임으로 둔다.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
