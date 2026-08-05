from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import IDMixin, TimestampMixin


class User(IDMixin, TimestampMixin, Base):
    """계정과 알림 동의. 자체 이메일+비밀번호 인증을 사용한다.

    사용자 삭제는 soft delete이며 일반 목록 조회는 is_deleted = false를 기본으로 한다.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    notification_agreed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
