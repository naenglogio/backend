from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
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


class EmailVerification(IDMixin, TimestampMixin, Base):
    """회원가입 전 이메일 소유 확인용 인증번호.

    users 테이블과 FK로 묶지 않는다 — 아직 계정이 존재하지 않는 이메일을 인증하는
    단계이기 때문이다. verified_at이 채워지고 EMAIL_VERIFICATION_SESSION_TTL_MINUTES
    이내인 레코드가 있어야 signup이 허용된다. 가입이 끝나면 해당 이메일의 레코드는 지운다.
    """

    __tablename__ = "email_verifications"

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
