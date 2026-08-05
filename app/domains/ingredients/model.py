from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import IDMixin, TimestampMixin
from app.domains.freshness.enums import ExpirationSource, ExpirationStatus, StorageType
from app.domains.ingredients.enums import DeletionReason


class Ingredient(IDMixin, TimestampMixin, Base):
    """사용자 냉장고 식재료.

    product_id/freshness_profile_id는 직접 입력 식재료를 위해 nullable이다.
    삭제는 soft delete이며 별도 삭제일시 컬럼 없이 updated_at을 사용한다.
    """

    __tablename__ = "ingredients"
    __table_args__ = (
        Index(
            "ix_ingredients_user_id_storage_type_expiration_date",
            "user_id",
            "storage_type",
            "expiration_date",
        ),
        Index("ix_ingredients_user_id_is_deleted", "user_id", "is_deleted"),
        CheckConstraint(
            "(is_deleted = false AND deletion_reason IS NULL) "
            "OR (is_deleted = true AND deletion_reason IS NOT NULL)",
            name="deletion_reason_matches_is_deleted",
        ),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_id: Mapped[int] = mapped_column(
        ForeignKey("foods.id", ondelete="RESTRICT"), nullable=False
    )
    # 직접 입력 식재료를 위해 nullable이다.
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    freshness_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_freshness_profiles.id", ondelete="SET NULL"), nullable=True
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
    expiration_date: Mapped[date] = mapped_column(Date, nullable=False)
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

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # 활성 상태에서는 null, 삭제 상태에서는 CONSUMED/DISCARDED/WRONG_ENTRY 중 하나다.
    deletion_reason: Mapped[DeletionReason | None] = mapped_column(
        SAEnum(
            DeletionReason,
            name="deletion_reason",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=True,
    )
