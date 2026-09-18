"""idempotent seed 적재/삭제 로직 (BE-6).

모든 생성은 natural key 기준 get-or-create라서 여러 번 실행해도 행이 늘어나지 않는다.
ingredient는 (user_id, name) — seed name이 행마다 유일하다.
"""

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seed import data
from app.domains.categories.model import Category
from app.domains.devices.model import Device
from app.domains.foods.model import Food
from app.domains.freshness.enums import ExpirationSource, ExpirationStatus, StorageType
from app.domains.freshness.model import ProductFreshnessProfile
from app.domains.freshness.service import (
    get_or_create_category,
    get_or_create_food,
    get_or_create_product,
)
from app.domains.ingredients.enums import DeletionReason
from app.domains.ingredients.model import Ingredient
from app.domains.notifications.model import Notification
from app.domains.products.enums import ProductSource
from app.domains.products.model import Product
from app.domains.users.model import User
from app.domains.users.service import hash_password, verify_password

logger = logging.getLogger(__name__)

_KST = timezone(timedelta(hours=9))


def _today_kst() -> date:
    return datetime.now(_KST).date()


async def _get_or_create_user(
    session: AsyncSession, email: str, nickname: str, notification_agreed: bool
) -> User:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is not None:
        # placeholder/옛 해시면 FE 로그인이 안 되므로 시드 비밀번호로만 맞춘다.
        if not verify_password(data.SEED_PASSWORD, user.password_hash):
            user.password_hash = hash_password(data.SEED_PASSWORD)
        user.nickname = nickname
        user.notification_agreed = notification_agreed
        await session.flush()
        return user
    user = User(
        email=email,
        password_hash=hash_password(data.SEED_PASSWORD),
        nickname=nickname,
        notification_agreed=notification_agreed,
        is_deleted=False,
    )
    session.add(user)
    await session.flush()
    return user


async def _get_or_create_device(session: AsyncSession, user_id: int, push_token: str) -> Device:
    result = await session.execute(select(Device).where(Device.push_token == push_token))
    device = result.scalar_one_or_none()
    if device is not None:
        return device
    device = Device(user_id=user_id, push_token=push_token)
    session.add(device)
    await session.flush()
    return device


async def _get_or_create_freshness_profile(
    session: AsyncSession, food_id: int, product_id: int, spec: dict[str, Any]
) -> ProductFreshnessProfile:
    result = await session.execute(
        select(ProductFreshnessProfile).where(
            ProductFreshnessProfile.food_id == food_id,
            ProductFreshnessProfile.product_id == product_id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is not None:
        return profile
    profile = ProductFreshnessProfile(
        food_id=food_id,
        product_id=product_id,
        storage_type=StorageType(spec["storage_type"]),
        expiration_days=spec["expiration_days"],
        expiration_source=ExpirationSource(spec["expiration_source"]),
        expiration_status=ExpirationStatus(spec["expiration_status"]),
    )
    session.add(profile)
    await session.flush()
    return profile


async def _get_or_create_ingredient(
    session: AsyncSession,
    *,
    spec: dict[str, Any],
    user_id: int,
    food_id: int,
    product_id: int | None,
    profile_id: int | None,
) -> Ingredient:
    # name이 seed 행마다 유일하므로 (user_id, name)으로 멱등을 보장한다.
    name = spec["name"]
    result = await session.execute(
        select(Ingredient).where(Ingredient.user_id == user_id, Ingredient.name == name)
    )
    ingredient = result.scalar_one_or_none()
    if ingredient is not None:
        return ingredient

    expiration_date = _today_kst() + timedelta(days=spec["expiration_offset_days"])
    deletion_reason = spec["deletion_reason"]
    ingredient = Ingredient(
        user_id=user_id,
        food_id=food_id,
        product_id=product_id,
        freshness_profile_id=profile_id,
        name=name,
        storage_type=int(spec["storage_type"]),
        quantity=int(spec.get("quantity", 1)),
        unit=spec.get("unit"),
        expiration_date=expiration_date,
        expiration_source=ExpirationSource(spec["expiration_source"]),
        expiration_status=ExpirationStatus(spec["expiration_status"]),
        image_url=spec.get("image_url"),
        memo=f"seed:{spec['key']}",
        is_deleted=spec["is_deleted"],
        deletion_reason=DeletionReason(deletion_reason) if deletion_reason else None,
    )
    session.add(ingredient)
    await session.flush()
    return ingredient


async def _get_or_create_notification(
    session: AsyncSession,
    *,
    user_id: int,
    ingredient_id: int | None,
    message: str,
    is_read: bool,
) -> Notification:
    result = await session.execute(
        select(Notification).where(Notification.user_id == user_id, Notification.message == message)
    )
    notification = result.scalar_one_or_none()
    if notification is not None:
        return notification
    notification = Notification(
        user_id=user_id, ingredient_id=ingredient_id, message=message, is_read=is_read
    )
    session.add(notification)
    await session.flush()
    return notification


async def run_seed(session: AsyncSession) -> None:
    """여러 번 실행해도 안전하다(natural key 기준 get-or-create)."""
    user_ids: dict[str, int] = {}
    for u in data.SEED_USERS:
        user = await _get_or_create_user(
            session, u["email"], u["nickname"], u["notification_agreed"]
        )
        user_ids[u["email"]] = user.id

    for dv in data.SEED_DEVICES:
        await _get_or_create_device(session, user_ids[dv["user_email"]], dv["push_token"])

    category_ids: dict[str, int] = {}
    for name in data.SEED_CATEGORY_NAMES:
        category = await get_or_create_category(session, name)
        category_ids[name] = category.id

    food_ids: dict[str, int] = {}
    for f in data.SEED_FOODS:
        food = await get_or_create_food(session, f["name"], category_ids[f["category_name"]])
        food_ids[f["name"]] = food.id

    product_ids: dict[str, int] = {}
    for p in data.SEED_PRODUCTS:
        product = await get_or_create_product(
            session,
            ProductSource(p["source"]),
            p["external_id"],
            p["name"],
            food_ids[p["food_name"]],
        )
        product_ids[p["external_id"]] = product.id

    profile_ids: dict[str, int] = {}
    for fp in data.SEED_FRESHNESS_PROFILES:
        food_id = food_ids[fp["food_name"]]
        product_id = product_ids[fp["product_external_id"]]
        profile = await _get_or_create_freshness_profile(session, food_id, product_id, fp)
        profile_ids[fp["product_external_id"]] = profile.id

    ingredient_ids: dict[str, int] = {}
    for spec in data.SEED_INGREDIENTS:
        food_id = food_ids[spec["food_name"]]
        ext_id = spec["product_external_id"]
        ingredient_product_id = product_ids[ext_id] if ext_id else None
        profile_id = profile_ids.get(ext_id) if spec["use_profile"] and ext_id else None
        ingredient = await _get_or_create_ingredient(
            session,
            spec=spec,
            user_id=user_ids[spec["user_email"]],
            food_id=food_id,
            product_id=ingredient_product_id,
            profile_id=profile_id,
        )
        ingredient_ids[spec["key"]] = ingredient.id

    for n in data.SEED_NOTIFICATIONS:
        await _get_or_create_notification(
            session,
            user_id=user_ids[n["user_email"]],
            ingredient_id=ingredient_ids.get(n["ingredient_key"]),
            message=n["message"],
            is_read=n["is_read"],
        )

    await session.commit()

    active_count = sum(1 for i in data.SEED_INGREDIENTS if not i["is_deleted"])
    logger.info(
        "Seed complete: users=%d devices=%d categories=%d foods=%d products=%d "
        "profiles=%d ingredients=%d (active=%d) notifications=%d",
        len(data.SEED_USERS),
        len(data.SEED_DEVICES),
        len(data.SEED_CATEGORY_NAMES),
        len(data.SEED_FOODS),
        len(data.SEED_PRODUCTS),
        len(data.SEED_FRESHNESS_PROFILES),
        len(data.SEED_INGREDIENTS),
        active_count,
        len(data.SEED_NOTIFICATIONS),
    )


async def reset_seed_data(session: AsyncSession) -> None:
    """이 스크립트가 만든 seed 데이터만 지운다. 삭제 범위는 고정된 식별자로 제한된다."""
    # 예전 도메인(@naenglog.local) 시드도 같이 치워 로컬 DB를 깨끗이 맞춘다.
    legacy_emails = [
        "seed.user1@naenglog.local",
        "seed.user2@naenglog.local",
        "seed.user3@naenglog.local",
    ]
    emails = list({*data.SEED_USER_EMAILS, *legacy_emails})
    await session.execute(delete(User).where(User.email.in_(emails)))

    food_names = [f["name"] for f in data.SEED_FOODS]
    product_external_ids = [p["external_id"] for p in data.SEED_PRODUCTS]
    legacy_product_ids = [
        "seed-prod-1001",
        "seed-prod-1002",
        "seed-prod-1003",
        "seed-prod-1004",
        "seed-prod-2001",
        "seed-prod-2002",
    ]
    all_product_ids = list({*product_external_ids, *legacy_product_ids})
    food_ids_subq = select(Food.id).where(Food.name.in_(food_names))

    await session.execute(
        delete(ProductFreshnessProfile).where(ProductFreshnessProfile.food_id.in_(food_ids_subq))
    )
    await session.execute(delete(Product).where(Product.external_id.in_(all_product_ids)))
    await session.execute(delete(Food).where(Food.name.in_(food_names)))
    await session.execute(delete(Category).where(Category.name.in_(data.SEED_CATEGORY_NAMES)))

    await session.commit()
    logger.info("Seed reset complete (scoped to known seed identifiers).")
