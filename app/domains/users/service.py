"""회원가입/로그인 업무 규칙과 transaction 경계.

비밀번호 해싱, JWT 발급/검증, 이메일 중복 체크를 담당한다. 인증된 사용자를
다른 요청에서 식별하는 방법(app.api.dependencies.get_current_user_id)은
이 모듈이 만드는 decode_access_token을 그대로 재사용하면 된다.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.mailer import send_email
from app.domains.users.model import EmailVerification, User
from app.domains.users.schema import EmailVerificationConfirm, LoginRequest, UserCreate


class EmailAlreadyRegisteredError(AppError):
    code = "EMAIL_ALREADY_REGISTERED"
    message = "이미 가입된 이메일입니다."
    status_code = 409


class InvalidCredentialsError(AppError):
    code = "INVALID_CREDENTIALS"
    message = "이메일 또는 비밀번호가 올바르지 않습니다."
    status_code = 401


class InvalidTokenError(AppError):
    code = "INVALID_TOKEN"
    message = "유효하지 않거나 만료된 토큰입니다."
    status_code = 401


class EmailNotVerifiedError(AppError):
    code = "EMAIL_NOT_VERIFIED"
    message = "이메일 인증을 먼저 완료해주세요."
    status_code = 400


class VerificationCooldownError(AppError):
    code = "VERIFICATION_COOLDOWN"
    message = "잠시 후 다시 시도해주세요."
    status_code = 429


class VerificationCodeExpiredError(AppError):
    code = "VERIFICATION_CODE_EXPIRED"
    message = "인증번호가 만료되었거나 존재하지 않습니다. 다시 요청해주세요."
    status_code = 400


class InvalidVerificationCodeError(AppError):
    code = "INVALID_VERIFICATION_CODE"
    message = "인증번호가 일치하지 않습니다."
    status_code = 400


class VerificationAttemptsExceededError(AppError):
    code = "VERIFICATION_ATTEMPTS_EXCEEDED"
    message = "시도 횟수를 초과했습니다. 인증번호를 다시 요청해주세요."
    status_code = 429


# bcrypt로 비밀번호 해싱
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# 비밀번호와 저장된 해시 일치 여부 확인
def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# user id를 담은 JWT access token 발급
def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# 토큰 검증 후 user id 반환. 만료·서명 불일치는 모두 InvalidTokenError로 통일
def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise InvalidTokenError() from exc

    subject = payload.get("sub")
    if subject is None:
        raise InvalidTokenError()
    return int(subject)


# 탈퇴하지 않은 사용자를 이메일로 조회
async def _get_active_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(
        select(User).where(User.email == email, User.is_deleted.is_(False))
    )
    return result.scalar_one_or_none()


# 6자리 인증번호 생성
def _generate_verification_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


# 인증번호를 평문으로 저장하지 않기 위해 해싱
def _hash_verification_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


# 인증번호 생성, 저장 후 이메일 발송. 재요청 쿨다운 안이면 거절
async def request_email_verification(session: AsyncSession, email: str) -> None:
    email = email.lower()
    now = datetime.now(UTC)

    result = await session.execute(
        select(EmailVerification)
        .where(EmailVerification.email == email)
        .order_by(EmailVerification.created_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    if latest is not None:
        cooldown_until = latest.created_at + timedelta(
            seconds=settings.EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS
        )
        if now < cooldown_until:
            raise VerificationCooldownError()

    code = _generate_verification_code()
    session.add(
        EmailVerification(
            email=email,
            code_hash=_hash_verification_code(code),
            expires_at=now + timedelta(minutes=settings.EMAIL_VERIFICATION_CODE_TTL_MINUTES),
        )
    )
    await session.commit()

    await send_email(
        to_email=email,
        subject="[냉로그] 이메일 인증번호",
        body=(
            f"인증번호는 {code}입니다. "
            f"{settings.EMAIL_VERIFICATION_CODE_TTL_MINUTES}분 안에 입력해주세요."
        ),
    )


# 인증번호 일치 여부 확인 후 verified_at 기록
async def confirm_email_verification(session: AsyncSession, data: EmailVerificationConfirm) -> None:
    email = data.email.lower()
    now = datetime.now(UTC)

    result = await session.execute(
        select(EmailVerification)
        .where(EmailVerification.email == email, EmailVerification.verified_at.is_(None))
        .order_by(EmailVerification.created_at.desc())
        .limit(1)
    )
    verification = result.scalar_one_or_none()
    if verification is None or verification.expires_at < now:
        raise VerificationCodeExpiredError()

    if verification.attempt_count >= settings.EMAIL_VERIFICATION_MAX_ATTEMPTS:
        raise VerificationAttemptsExceededError()

    if verification.code_hash != _hash_verification_code(data.code):
        verification.attempt_count += 1
        await session.commit()
        raise InvalidVerificationCodeError()

    verification.verified_at = now
    await session.commit()


# 유효 시간 안의 인증 완료 기록 조회
async def _get_verified_email_verification(
    session: AsyncSession, email: str
) -> EmailVerification | None:
    now = datetime.now(UTC)
    session_expiry_floor = now - timedelta(minutes=settings.EMAIL_VERIFICATION_SESSION_TTL_MINUTES)

    result = await session.execute(
        select(EmailVerification)
        .where(
            EmailVerification.email == email,
            EmailVerification.verified_at.is_not(None),
            EmailVerification.verified_at >= session_expiry_floor,
        )
        .order_by(EmailVerification.verified_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# 이메일 인증 완료 시에만 계정 생성, 사용한 인증 기록은 삭제
async def signup(session: AsyncSession, data: UserCreate) -> User:
    email = data.email.lower()
    if await _get_active_user_by_email(session, email) is not None:
        raise EmailAlreadyRegisteredError()

    if await _get_verified_email_verification(session, email) is None:
        raise EmailNotVerifiedError()

    user = User(email=email, password_hash=hash_password(data.password))
    session.add(user)
    # 검증 세션은 1회용으로 소비한다 — 가입이 끝나면 같은 이메일의 인증 기록은 지운다.
    await session.execute(delete(EmailVerification).where(EmailVerification.email == email))
    await session.commit()
    await session.refresh(user)
    return user


# 이메일/비밀번호 검증 후 access token 발급
async def login(session: AsyncSession, data: LoginRequest) -> str:
    user = await _get_active_user_by_email(session, data.email.lower())
    if user is None or not verify_password(data.password, user.password_hash):
        raise InvalidCredentialsError()

    return create_access_token(user.id)
