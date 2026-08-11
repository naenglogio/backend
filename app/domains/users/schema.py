"""회원가입/로그인 Pydantic 요청·응답 계약.

model.py의 ORM 컬럼(password_hash 등)을 그대로 노출하지 않는다.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    # bcrypt는 72바이트를 넘는 입력을 다루지 못하므로 상한을 둔다.
    password: str = Field(min_length=8, max_length=72)
    nickname: str = Field(min_length=1, max_length=20)


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nickname: str
    notification_agreed: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
