from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import IDMixin, TimestampMixin


class Notification(IDMixin, TimestampMixin, Base):
    """알림 내역.

    ingredient_id는 SET NULL로 둬서, 식재료 행이 사라져도(soft delete 기준으로는
    발생하지 않지만) 알림 이력 자체는 삭제되지 않게 한다.
    """

    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredients.id", ondelete="SET NULL"), nullable=True
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
