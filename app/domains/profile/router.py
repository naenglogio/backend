from fastapi import APIRouter, Query, status

from app.api.dependencies import CurrentUserId, DBSession
from app.api.schemas import COMMON_ERROR_RESPONSES
from app.domains.profile.schema import (
    IngredientUsageStats,
    NicknameUpdate,
    NotificationAgreementUpdate,
    PasswordUpdate,
    ProfileRead,
)
from app.domains.profile.service import (
    get_ingredient_usage_stats,
    get_profile,
    update_nickname,
    update_notification_agreement,
    update_password,
)

router = APIRouter()


# 내정보 조회
@router.get("/me", response_model=ProfileRead, responses=COMMON_ERROR_RESPONSES)
async def get_profile_route(user_id: CurrentUserId, session: DBSession) -> ProfileRead:
    user = await get_profile(session, user_id)
    return ProfileRead.model_validate(user)


# 닉네임 변경
@router.patch("/nickname", response_model=ProfileRead, responses=COMMON_ERROR_RESPONSES)
async def update_nickname_route(
    data: NicknameUpdate, user_id: CurrentUserId, session: DBSession
) -> ProfileRead:
    user = await update_nickname(session, user_id, data.nickname)
    return ProfileRead.model_validate(user)


# 비밀번호 변경
@router.patch(
    "/password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"description": "현재 비밀번호 불일치"}, **COMMON_ERROR_RESPONSES},
)
async def update_password_route(
    data: PasswordUpdate, user_id: CurrentUserId, session: DBSession
) -> None:
    await update_password(session, user_id, data.current_password, data.new_password)


# 알림 수신 동의 여부 변경
@router.patch(
    "/notification-agreement",
    response_model=ProfileRead,
    responses=COMMON_ERROR_RESPONSES,
)
async def update_notification_agreement_route(
    data: NotificationAgreementUpdate, user_id: CurrentUserId, session: DBSession
) -> ProfileRead:
    user = await update_notification_agreement(session, user_id, data.notification_agreed)
    return ProfileRead.model_validate(user)


# 기간별 식재료 사용/폐기 통계 (자주 쓰는/자주 버리는 식재료)
@router.get(
    "/ingredient-stats",
    response_model=IngredientUsageStats,
    responses=COMMON_ERROR_RESPONSES,
)
async def get_ingredient_usage_stats_route(
    user_id: CurrentUserId,
    session: DBSession,
    days: int = Query(default=7, ge=1, le=365, description="조회할 기간(일). 예: 1=당일, 3, 7, 30"),
) -> IngredientUsageStats:
    return await get_ingredient_usage_stats(session, user_id, days)
