"""ingredients DB 질의 계층.

ORM은 이 모듈에서만 사용한다 (router 금지).
"""

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.categories.model import Category
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

    total = await session.scalar(select(func.count()).select_from(Ingredient).where(*conditions))

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
        select(ProductFreshnessProfile).where(ProductFreshnessProfile.id == freshness_profile_id)
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

    BE-5: 카운트는 한 번의 집계 쿼리(COUNT FILTER)로, 임박 목록은 정렬·limit이
    필요하므로 별도 쿼리로 가져온다. 임박 판정 기준일(today)과 임계 일수는 업무
    규칙이라 service가 넘겨주고, 여기서는 받은 값으로 질의만 한다.

    임박 조건은 `expiration_date <= today + expiring_within_days`이므로 이미 지난
    항목도 포함된다(대시보드에서 가장 먼저 조치해야 할 대상이다).
    expiration_date가 null(소비기한 미확정)이면 임박으로 세지 않되 total에는 포함된다.
    """
    threshold = today + timedelta(days=expiring_within_days)
    conditions = [Ingredient.user_id == user_id, Ingredient.is_deleted.is_(False)]
    expiring_conditions = [
        Ingredient.expiration_date.is_not(None),
        Ingredient.expiration_date <= threshold,
    ]

    counts = (
        await session.execute(
            select(
                func.count(),
                func.count().filter(Ingredient.storage_type == 0),
                func.count().filter(Ingredient.storage_type == 1),
                func.count().filter(*expiring_conditions),
            )
            .select_from(Ingredient)
            .where(*conditions)
        )
    ).one()
    total, refrigerated_count, frozen_count, expiring_count = counts

    # 급한 것부터. 같은 날짜면 id로 순서를 고정해 페이지 재요청 시 결과가 흔들리지 않게 한다.
    expiring_rows = await session.execute(
        select(
            Ingredient.id,
            Ingredient.name,
            Ingredient.storage_type,
            Ingredient.expiration_date,
        )
        .where(*conditions, *expiring_conditions)
        .order_by(Ingredient.expiration_date.asc(), Ingredient.id.asc())
        .limit(expiring_top_n)
    )

    return {
        "total": total,
        "refrigerated_count": refrigerated_count,
        "frozen_count": frozen_count,
        "expiring_count": expiring_count,
        "expiring_items": [
            {
                "id": row.id,
                "name": row.name,
                "storage_type": row.storage_type,
                "expiration_date": row.expiration_date,
            }
            for row in expiring_rows
        ],
    }


async def list_foods_with_categories_by_names(
    session: AsyncSession,
    *,
    names: list[str],
) -> dict[str, tuple[int, str | None]]:
    """food.name → (food_id, category_name). 인식 후보 food_id 매칭용.

    같은 이름이 여러 건이면 먼저 나온 것을 쓴다(seed는 name 유일).
    """
    if not names:
        return {}
    result = await session.execute(
        select(Food.id, Food.name, Category.name)
        .join(Category, Category.id == Food.category_id)
        .where(Food.name.in_(names))
    )
    mapping: dict[str, tuple[int, str | None]] = {}
    for food_id, food_name, category_name in result.all():
        mapping.setdefault(food_name, (food_id, category_name))
    return mapping


async def list_recognition_catalog(
    session: AsyncSession,
) -> tuple[list[tuple[int, str, str | None]], list[tuple[int, str, str, int, str, str | None]]]:
    """인식용 카탈로그: foods + (비활성 제외) products.

    반환:
    - foods: (food_id, food_name, category_name)
    - products: (product_id, external_id, product_name, food_id, food_name, category_name)
    """
    food_rows = await session.execute(
        select(Food.id, Food.name, Category.name)
        .join(Category, Category.id == Food.category_id)
        .order_by(Food.id.asc())
    )
    foods = [(food_id, food_name, category_name) for food_id, food_name, category_name in food_rows]

    product_rows = await session.execute(
        select(
            Product.id,
            Product.external_id,
            Product.name,
            Food.id,
            Food.name,
            Category.name,
        )
        .join(Food, Food.id == Product.food_id)
        .join(Category, Category.id == Food.category_id)
        .where(Product.external_id != "MOCK-INACTIVE")
        .order_by(Product.id.asc())
    )
    products = [
        (product_id, external_id, product_name, food_id, food_name, category_name)
        for product_id, external_id, product_name, food_id, food_name, category_name in product_rows
    ]
    return foods, products
