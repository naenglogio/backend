from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import IDMixin, TimestampMixin
from app.domains.products.enums import ProductSource


class Product(IDMixin, TimestampMixin, Base):
    """컬리N마트 상품 식별.

    가격은 서비스 요구사항이 아니므로 컬럼을 두지 않는다.
    """

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_products_source_external_id"),
    )

    food_id: Mapped[int] = mapped_column(
        ForeignKey("foods.id", ondelete="RESTRICT"), nullable=False
    )
    source: Mapped[ProductSource] = mapped_column(
        SAEnum(
            ProductSource,
            name="source",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
