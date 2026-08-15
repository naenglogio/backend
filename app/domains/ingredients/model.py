from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import IDMixin, TimestampMixin
from app.domains.freshness.enums import ExpirationSource, ExpirationStatus
from app.domains.ingredients.enums import DeletionReason


class Ingredient(IDMixin, TimestampMixin, Base):
    """사용자 냉장고 식재료.

    BE-1: 노션 ERD #7 / shared/00_API_CONTRACT.md 정본에 맞춘 스키마.
    product_id/freshness_profile_id는 직접 입력 식재료를 위해 nullable이다.
    storage_type은 int(0=냉장, 1=냉동)다. (문자열 enum 아님)
    삭제는 soft delete이며 별도 삭제일시 컬럼 없이 updated_at을 사용한다.
    """

    __tablename__ = "ingredients"
    __table_args__ = (
        # 목록 필터(보관방식·소비기한)용 복합 인덱스
        Index(
            "ix_ingredients_user_id_storage_type_expiration_date",
            "user_id",
            "storage_type",
            "expiration_date",
        ),
        # 활성 식재료만 조회할 때 사용
        Index("ix_ingredients_user_id_is_deleted", "user_id", "is_deleted"),
        # soft delete 일관성: 삭제 안 됨 ↔ 사유 null / 삭제됨 ↔ 사유 필수
        CheckConstraint(
            "(is_deleted = false AND deletion_reason IS NULL) "
            "OR (is_deleted = true AND deletion_reason IS NOT NULL)",
            name="deletion_reason_matches_is_deleted",
        ),
        # BE-1: storage_type은 0(냉장)/1(냉동)만 허용. ROOM_TEMPERATURE 제거.
        CheckConstraint(
            "storage_type IN (0, 1)",
            name="storage_type_is_refrigerated_or_frozen",
        ),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_id: Mapped[int] = mapped_column(
        ForeignKey("foods.id", ondelete="RESTRICT"), nullable=False
    )
    # 직접 입력 식재료(상품 없이 등록)면 null
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    # 직접 입력이거나 프로필 미연결이면 null
    freshness_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_freshness_profiles.id", ondelete="SET NULL"), nullable=True
    )

    # --- BE-1에서 추가한 필드 (노션 ERD 누락분) ---
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # 화면 표시용 식재료 이름
    # 0=냉장, 1=냉동 (API 계약서 정본). 예전 문자열 REFRIGERATED/FROZEN/ROOM_TEMPERATURE 대체.
    storage_type: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # 수량, 기본 1
    unit: Mapped[str | None] = mapped_column(String(30), nullable=True)  # 단위(개, g 등), 선택
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)  # 구매일, 선택
    # 계약서상 nullable. 아직 모를 수 있음.
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # 소비기한 출처. 기본값 USER_INPUT(사용자가 직접 입력)
    expiration_source: Mapped[ExpirationSource] = mapped_column(
        SAEnum(
            ExpirationSource,
            name="expiration_source",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
        default=ExpirationSource.USER_INPUT,
    )
    # 소비기한 신뢰도. 기본값 CONFIRMED(확정)
    expiration_status: Mapped[ExpirationStatus] = mapped_column(
        SAEnum(
            ExpirationStatus,
            name="expiration_status",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
        default=ExpirationStatus.CONFIRMED,
    )
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)  # 사진 URL, 선택
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)  # 메모, 선택

    # False=보유 중 / True=논리 삭제(목록에서 숨김)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # is_deleted=false면 null, true면 CONSUMED(먹음)/DISCARDED(버림)/INCORRECT_ENTRY(잘못 등록) 중 하나.
    # BE-1: 예전 값 WRONG_ENTRY → INCORRECT_ENTRY로 정본 변경.
    deletion_reason: Mapped[DeletionReason | None] = mapped_column(
        SAEnum(
            DeletionReason,
            name="deletion_reason",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=True,
    )
