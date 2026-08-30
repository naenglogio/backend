"""내정보 업무 규칙.

알림 동의 변경은 users.notification_agreed를 직접 갱신한다 — 실제 알림 발송
여부는 이 값을 읽는 쪽(notifications 도메인)의 책임이고, 여기서는 값만 정확히
유지한다. 식재료 통계는 ingredients를 조회만 하고 변경하지 않는다
(freshness/service.py가 다른 도메인 모델을 다루는 것과 같은 패턴).
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, NotFoundError
from app.domains.foods.model import Food
from app.domains.ingredients.enums import DeletionReason
from app.domains.ingredients.model import Ingredient
from app.domains.profile.schema import IngredientUsageItem, IngredientUsageStats
from app.domains.users.model import User
from app.domains.users.service import hash_password, verify_password


class CurrentPasswordMismatchError(AppError):
    code = "CURRENT_PASSWORD_MISMATCH"
    message = "현재 비밀번호가 일치하지 않습니다."
    status_code = 401


async def _get_active_user(session: AsyncSession, user_id: int) -> User:
    user = await session.get(User, user_id)
    if user is None or user.is_deleted:
        raise NotFoundError(message="사용자를 찾을 수 없습니다.")
    return user


# 내정보 화면 진입 시 현재 프로필 조회
async def get_profile(session: AsyncSession, user_id: int) -> User:
    return await _get_active_user(session, user_id)


# 알림 수신 동의 여부 변경
async def update_notification_agreement(session: AsyncSession, user_id: int, agreed: bool) -> User:
    user = await _get_active_user(session, user_id)
    user.notification_agreed = agreed
    await session.commit()
    await session.refresh(user)
    return user


# 닉네임 변경
async def update_nickname(session: AsyncSession, user_id: int, nickname: str) -> User:
    user = await _get_active_user(session, user_id)
    user.nickname = nickname
    await session.commit()
    await session.refresh(user)
    return user


# 비밀번호 변경. 탈취된 토큰만으로 바꿀 수 없도록 현재 비밀번호 확인을 요구한다.
async def update_password(
    session: AsyncSession, user_id: int, current_password: str, new_password: str
) -> None:
    user = await _get_active_user(session, user_id)
    if not verify_password(current_password, user.password_hash):
        raise CurrentPasswordMismatchError()

    user.password_hash = hash_password(new_password)
    await session.commit()


# 최근 N일간 식재료 사용(CONSUMED)/폐기(DISCARDED) 횟수를 식재료별로 집계
async def get_ingredient_usage_stats(
    session: AsyncSession, user_id: int, days: int
) -> IngredientUsageStats:
    cutoff = datetime.now(UTC) - timedelta(days=days)

    consumed_count = func.count().filter(Ingredient.deletion_reason == DeletionReason.CONSUMED)
    discarded_count = func.count().filter(Ingredient.deletion_reason == DeletionReason.DISCARDED)

    result = await session.execute(
        select(Ingredient.food_id, Food.name, consumed_count, discarded_count)
        .select_from(Ingredient)
        .join(Food, Food.id == Ingredient.food_id)
        .where(
            Ingredient.user_id == user_id,
            Ingredient.is_deleted.is_(True),
            # WRONG_ENTRY(오등록 취소)는 실제 사용/폐기가 아니므로 통계에서 뺀다.
            Ingredient.deletion_reason.in_([DeletionReason.CONSUMED, DeletionReason.DISCARDED]),
            Ingredient.updated_at >= cutoff,
        )
        .group_by(Ingredient.food_id, Food.name)
    )

    items = [
        IngredientUsageItem(
            food_id=food_id, food_name=food_name, consumed_count=consumed, discarded_count=discarded
        )
        for food_id, food_name, consumed, discarded in result.all()
    ]

    most_used = max(
        (item for item in items if item.consumed_count > 0),
        key=lambda item: item.consumed_count,
        default=None,
    )
    most_discarded = max(
        (item for item in items if item.discarded_count > 0),
        key=lambda item: item.discarded_count,
        default=None,
    )

    return IngredientUsageStats(
        period_days=days, most_used=most_used, most_discarded=most_discarded, items=items
    )
