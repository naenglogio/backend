"""내정보(닉네임/비밀번호 변경, 알림 동의, 식재료 통계) Pydantic 요청·응답 계약."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class NotificationAgreementUpdate(BaseModel):
    notification_agreed: bool


class NicknameUpdate(BaseModel):
    nickname: str = Field(min_length=1, max_length=20)


class PasswordUpdate(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    # bcrypt는 72바이트를 넘는 입력을 다루지 못하므로 상한을 둔다. (signup과 동일)
    new_password: str = Field(min_length=8, max_length=72)


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nickname: str
    notification_agreed: bool


class IngredientUsageItem(BaseModel):
    food_id: int
    food_name: str
    consumed_count: int
    discarded_count: int


class IngredientUsageStats(BaseModel):
    period_days: int
    # 조회 기간 안에 사용/폐기 기록이 없으면 null.
    most_used: IngredientUsageItem | None
    most_discarded: IngredientUsageItem | None
    items: list[IngredientUsageItem]
