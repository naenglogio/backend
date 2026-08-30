from fastapi import APIRouter, status

from app.api.dependencies import DBSession
from app.api.schemas import COMMON_ERROR_RESPONSES
from app.domains.users.schema import (
    EmailVerificationConfirm,
    EmailVerificationRequest,
    LoginRequest,
    PasswordResetComplete,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
    UserCreate,
    UserRead,
)
from app.domains.users.service import complete_password_reset, confirm_email_verification
from app.domains.users.service import confirm_password_reset as confirm_password_reset_service
from app.domains.users.service import login as login_user
from app.domains.users.service import request_email_verification, request_password_reset
from app.domains.users.service import signup as signup_user

router = APIRouter()


# 이메일로 인증번호 발송
@router.post(
    "/email-verifications",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        409: {"description": "이미 가입된 이메일"},
        429: {"description": "너무 잦은 재요청"},
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_email_verification(data: EmailVerificationRequest, session: DBSession) -> None:
    await request_email_verification(session, data.email)


# 발송된 인증번호가 맞는지 확인
@router.post(
    "/email-verifications/confirm",
    responses={
        400: {"description": "인증번호 불일치 또는 만료"},
        429: {"description": "시도 횟수 초과"},
        **COMMON_ERROR_RESPONSES,
    },
)
async def confirm_email_verification_code(
    data: EmailVerificationConfirm, session: DBSession
) -> dict[str, bool]:
    await confirm_email_verification(session, data)
    return {"verified": True}


# 이메일 인증이 끝난 사용자만 회원가입 처리
@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "이메일 인증 미완료"},
        409: {"description": "이미 가입된 이메일"},
        **COMMON_ERROR_RESPONSES,
    },
)
async def signup(data: UserCreate, session: DBSession) -> UserRead:
    user = await signup_user(session, data)
    return UserRead.model_validate(user)


# 이메일/비밀번호를 검증하고 access token 발급
@router.post(
    "/login",
    response_model=Token,
    responses={401: {"description": "이메일 또는 비밀번호 불일치"}, **COMMON_ERROR_RESPONSES},
)
async def login(data: LoginRequest, session: DBSession) -> Token:
    access_token = await login_user(session, data)
    return Token(access_token=access_token)


# 비밀번호 재설정 인증번호 발송. 가입 여부와 무관하게 항상 202를 반환한다
# (계정 존재 여부를 노출하지 않기 위함).
@router.post(
    "/password-resets",
    status_code=status.HTTP_202_ACCEPTED,
    responses={429: {"description": "너무 잦은 재요청"}, **COMMON_ERROR_RESPONSES},
)
async def create_password_reset(data: PasswordResetRequest, session: DBSession) -> None:
    await request_password_reset(session, data.email)


# 발송된 비밀번호 재설정 인증번호가 맞는지 확인
@router.post(
    "/password-resets/confirm",
    responses={
        400: {"description": "인증번호 불일치 또는 만료"},
        429: {"description": "시도 횟수 초과"},
        **COMMON_ERROR_RESPONSES,
    },
)
async def confirm_password_reset(data: PasswordResetConfirm, session: DBSession) -> dict[str, bool]:
    await confirm_password_reset_service(session, data)
    return {"verified": True}


# 인증이 끝난 사용자만 새 비밀번호로 변경
@router.post(
    "/password-resets/complete",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"description": "인증 미완료"}, **COMMON_ERROR_RESPONSES},
)
async def complete_password_reset_endpoint(data: PasswordResetComplete, session: DBSession) -> None:
    await complete_password_reset(session, data)
