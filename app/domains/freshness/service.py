"""정제 완료 데이터를 검증·매핑해 저장하는 규칙.

app/batch/freshness_data_import.py가 이 모듈을 호출해 실제 저장을 위임한다.
이 모듈은 실행 순서나 재시도를 알지 못하고, 레코드 하나를 어떻게 우리 스키마에
맞출지만 안다.
"""

import logging
import math

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.categories.model import Category
from app.domains.foods.model import Food
from app.domains.freshness.contracts import RefinedFreshnessRecord
from app.domains.freshness.enums import ExpirationSource, ExpirationStatus, StorageType
from app.domains.freshness.model import ProductFreshnessProfile
from app.domains.products.enums import ProductSource
from app.domains.products.model import Product

logger = logging.getLogger(__name__)

# food_name만 있고 category 정보가 없는 정제 레코드를 위한 기본 분류.
# 실제 카테고리 매핑이 파이프라인 계약에 추가되면 이 fallback은 없앤다.
UNCLASSIFIED_CATEGORY_NAME = "미분류"

# 파이프라인 selected_source(KURLY/MFDS/MANUAL, gold_freshness 계약) -> 도메인 enum 매핑.
# 알려지지 않은 값은 보수적으로 PRODUCT_DISCLOSURE로 두고 로그를 남긴다.
_EXPIRATION_SOURCE_MAP: dict[str, ExpirationSource] = {
    "KURLY": ExpirationSource.PRODUCT_DISCLOSURE,
    "MFDS": ExpirationSource.MFDS_REFERENCE,
    "MANUAL": ExpirationSource.USER_INPUT,
}
# YEAR/HOUR은 gold_freshness.expiration_unit 계약에 있지만 이전엔 누락돼 있었다.
# HOUR은 배수로 표현할 수 없어 _map_expiration_days에서 별도로 올림(ceil) 처리한다.
_UNIT_TO_DAYS = {"DAY": 1, "WEEK": 7, "MONTH": 30, "YEAR": 365}
_CONFIDENCE_CONFIRMED_THRESHOLD = 0.8


def _map_expiration_source(raw_source: str) -> ExpirationSource:
    mapped = _EXPIRATION_SOURCE_MAP.get(raw_source.upper())
    if mapped is None:
        logger.warning(
            "Unknown freshness expiration_source '%s', defaulting to PRODUCT_DISCLOSURE",
            raw_source,
        )
        return ExpirationSource.PRODUCT_DISCLOSURE
    return mapped


def _map_expiration_status(confidence: float, review_status: str) -> ExpirationStatus:
    if review_status.upper() != "APPROVED":
        return ExpirationStatus.REVIEW_REQUIRED
    if confidence >= _CONFIDENCE_CONFIRMED_THRESHOLD:
        return ExpirationStatus.CONFIRMED
    return ExpirationStatus.ESTIMATED


def _map_expiration_days(value: int, unit: str) -> int:
    unit_upper = unit.upper()
    if unit_upper == "HOUR":
        # 시간 단위는 배수로 표현되지 않는다. 내림(floor)하면 '이미 지남'처럼
        # 보일 수 있어(예: 12시간 -> 0일) 최소 1일을 보장하며 올림한다.
        return max(1, math.ceil(value / 24))
    multiplier = _UNIT_TO_DAYS.get(unit_upper)
    if multiplier is None:
        raise ValueError(f"지원하지 않는 expiration_unit: {unit}")
    return math.ceil(value * multiplier)


def _map_storage_type(raw_storage_type: str) -> StorageType:
    try:
        return StorageType(raw_storage_type.upper())
    except ValueError as exc:
        raise ValueError(f"지원하지 않는 storage_type: {raw_storage_type}") from exc


async def get_or_create_category(session: AsyncSession, name: str) -> Category:
    result = await session.execute(select(Category).where(Category.name == name))
    category = result.scalar_one_or_none()
    if category is not None:
        return category
    category = Category(name=name)
    session.add(category)
    await session.flush()
    return category


async def get_or_create_food(session: AsyncSession, name: str, category_id: int) -> Food:
    result = await session.execute(select(Food).where(Food.name == name))
    food = result.scalar_one_or_none()
    if food is not None:
        return food
    food = Food(name=name, category_id=category_id)
    session.add(food)
    await session.flush()
    return food


async def get_or_create_product(
    session: AsyncSession,
    source: ProductSource,
    external_id: str,
    name: str,
    food_id: int,
) -> Product:
    result = await session.execute(
        select(Product).where(Product.source == source, Product.external_id == external_id)
    )
    product = result.scalar_one_or_none()
    if product is not None:
        return product
    product = Product(source=source, external_id=external_id, name=name, food_id=food_id)
    session.add(product)
    await session.flush()
    return product


async def upsert_freshness_profile(
    session: AsyncSession,
    *,
    food_id: int,
    product_id: int | None,
    storage_type: StorageType,
    expiration_days: int,
    expiration_source: ExpirationSource,
    expiration_status: ExpirationStatus,
) -> ProductFreshnessProfile:
    """같은 (food_id, product_id) 조합이 있으면 최신 정제 결과로 갱신하고, 없으면 새로 만든다."""
    result = await session.execute(
        select(ProductFreshnessProfile).where(
            ProductFreshnessProfile.food_id == food_id,
            ProductFreshnessProfile.product_id == product_id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = ProductFreshnessProfile(food_id=food_id, product_id=product_id)
        session.add(profile)

    profile.storage_type = storage_type
    profile.expiration_days = expiration_days
    profile.expiration_source = expiration_source
    profile.expiration_status = expiration_status
    await session.flush()
    return profile


async def import_refined_record(
    session: AsyncSession, record: RefinedFreshnessRecord
) -> ProductFreshnessProfile:
    """정제 완료 레코드 하나를 검증·매핑해 저장한다.

    실행 순서·재시도 같은 orchestration은 호출자(app/batch)의 책임이다.
    """
    storage_type = _map_storage_type(record.storage_type)
    expiration_days = _map_expiration_days(record.expiration_value, record.expiration_unit)
    expiration_source = _map_expiration_source(record.source)
    expiration_status = _map_expiration_status(record.confidence, record.review_status)

    category = await get_or_create_category(session, UNCLASSIFIED_CATEGORY_NAME)
    food = await get_or_create_food(session, record.food_name, category.id)
    product = await get_or_create_product(
        session,
        record.product_source,
        record.external_product_id,
        record.product_name,
        food.id,
    )

    return await upsert_freshness_profile(
        session,
        food_id=food.id,
        product_id=product.id,
        storage_type=storage_type,
        expiration_days=expiration_days,
        expiration_source=expiration_source,
        expiration_status=expiration_status,
    )
