from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import IDMixin, TimestampMixin
from app.domains.freshness.enums import ExpirationSource, ExpirationStatus, StorageType


class ProductFreshnessProfile(IDMixin, TimestampMixin, Base):
    """데이터 파이프라인이 정제한 보관 방식·소비기한 결과.

    원문 파일이나 OCR/정제 중간 산출물은 여기 저장하지 않는다(별도 파이프라인 저장소 책임).
    """

    __tablename__ = "product_freshness_profiles"
    __table_args__ = (
        Index("ix_product_freshness_profiles_food_id", "food_id"),
        Index("ix_product_freshness_profiles_product_id", "product_id"),
        Index("ix_product_freshness_profiles_expiration_status", "expiration_status"),
    )

    food_id: Mapped[int] = mapped_column(
        ForeignKey("foods.id", ondelete="RESTRICT"), nullable=False
    )
    # 특정 상품이 아니라 식품 일반에 대한 결과일 수 있어 nullable이다.
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )

    storage_type: Mapped[StorageType] = mapped_column(
        SAEnum(
            StorageType,
            name="storage_type",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )
    expiration_days: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    expiration_source: Mapped[ExpirationSource] = mapped_column(
        SAEnum(
            ExpirationSource,
            name="expiration_source",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )
    expiration_status: Mapped[ExpirationStatus] = mapped_column(
        SAEnum(
            ExpirationStatus,
            name="expiration_status",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )
