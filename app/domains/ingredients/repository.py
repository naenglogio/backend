"""ingredients DB 질의 계층.

ORM은 이 모듈에서만 사용한다 (router 금지).
"""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.foods.model import Food
from app.domains.freshness.enums import ExpirationStatus
from app.domains.freshness.model import ProductFreshnessProfile
from app.domains.ingredients.model import Ingredient
from app.domains.products.model import Product


async def list_active_by_user(
    session: AsyncSession,
    *,
    user_id: int,
    storage_type: int | None = None,
    expiration_status: ExpirationStatus | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Ingredient], int]:
    """소유분·is_deleted=false 목록과 total.

    BE-3: storage_type·expiration_status는 optional 필터. 최근 등록순으로 정렬한다.
    """
    conditions = [Ingredient.user_id == user_id, Ingredient.is_deleted.is_(False)]
    if storage_type is not None:
        conditions.append(Ingredient.storage_type == storage_type)
    if expiration_status is not None:
        conditions.append(Ingredient.expiration_status == expiration_status)

    total = await session.scalar(
        select(func.count()).select_from(Ingredient).where(*conditions)
    )

    result = await session.execute(
        select(Ingredient)
        .where(*conditions)
        .order_by(Ingredient.created_at.desc(), Ingredient.id.desc())
        .offset(offset)
        .limit(limit)
    )
    items = list(result.scalars().all())
    return items, total or 0


async def get_owned_by_id(
    session: AsyncSession,
    *,
    user_id: int,
    ingredient_id: int,
) -> Ingredient | None:
    """본인 소유·미삭제 ingredient 단건. 없거나 남의 것이면 None → service에서 404.

    is_deleted=true인 항목도 소유권과 무관하게 목록에서 이미 숨겨져 있으므로
    상세 조회에서도 동일하게 404 취급한다(목록과 상세의 가시성 일치).
    """
    result = await session.execute(
        select(Ingredient).where(
            Ingredient.id == ingredient_id,
            Ingredient.user_id == user_id,
            Ingredient.is_deleted.is_(False),
        )
    )
    return result.scalar_one_or_none()


async def get_product_by_id(
    session: AsyncSession,
    *,
    product_id: int,
) -> Product | None:
    """상세 응답 nested product용."""
    result = await session.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def get_freshness_profile_by_id(
    session: AsyncSession,
    *,
    freshness_profile_id: int,
) -> ProductFreshnessProfile | None:
    """상세 응답 nested freshness_profile용."""
    result = await session.execute(
        select(ProductFreshnessProfile).where(
            ProductFreshnessProfile.id == freshness_profile_id
        )
    )
    return result.scalar_one_or_none()


async def get_food_by_id(
    session: AsyncSession,
    *,
    food_id: int,
) -> Food | None:
    """등록 시 food_id 참조 무결성 확인용."""
    result = await session.execute(select(Food).where(Food.id == food_id))
    return result.scalar_one_or_none()


async def create(
    session: AsyncSession,
    ingredient: Ingredient,
) -> Ingredient:
    """식재료 행 추가 후 flush한 엔티티 반환. commit 경계는 service가 담당한다."""
    session.add(ingredient)
    await session.flush()
    return ingredient


async def summarize_active_by_user(
    session: AsyncSession,
    *,
    user_id: int,
    today: date,
    expiring_within_days: int,
    expiring_top_n: int,
) -> dict[str, object]:
    """대시보드 집계용 raw 결과.

    BE-5: total / refrigerated_count / frozen_count / expiring_count / expiring_items
    를 채워 반환. 키 이름은 service가 IngredientSummaryResponse로 매핑한다.
    """
    raise NotImplementedError("BE-5에서 구현")
