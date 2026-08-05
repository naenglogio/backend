from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import IDMixin, TimestampMixin


class Device(IDMixin, TimestampMixin, Base):
    """사용자별 푸시 토큰."""

    __tablename__ = "devices"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    push_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
