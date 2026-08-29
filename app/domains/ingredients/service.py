"""ingredients 업무 규칙과 transaction 경계.

DB는 repository에 위임하고, 여기서는 소유권·기본값·매핑 규칙을 담당한다.
실제 로직은 BE-3(목록·상세), BE-4(등록), BE-5(집계), BE-7(인식)에서 채운다.
"""

from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import Page
from app.core.exceptions import AppError
from app.domains.freshness.enums import ExpirationStatus
from app.domains.freshness.model import ProductFreshnessProfile
from app.domains.ingredients import repository
from app.domains.ingredients.model import Ingredient as IngredientModel
from app.domains.ingredients.schema import (
    CameraRecognizeResponse,
    Ingredient,
    IngredientCreateRequest,
    IngredientDetailResponse,
    IngredientSummaryResponse,
    ProductFreshnessProfileRead,
    ProductRead,
)


class IngredientNotFoundError(AppError):
    """없거나 남의 식재료에 접근할 때. 계약서상 404로 통일."""

    code = "INGREDIENT_NOT_FOUND"
    message = "식재료를 찾을 수 없습니다."
    status_code = 404


class FoodNotFoundError(AppError):
    """등록 요청의 food_id가 존재하지 않을 때."""

    code = "FOOD_NOT_FOUND"
    message = "식품 정보를 찾을 수 없습니다."
    status_code = 422


class ProductNotFoundError(AppError):
    """등록 요청의 product_id가 존재하지 않을 때."""

    code = "PRODUCT_NOT_FOUND"
    message = "상품 정보를 찾을 수 없습니다."
    status_code = 422


class FreshnessProfileNotFoundError(AppError):
    """등록 요청의 freshness_profile_id가 존재하지 않을 때."""

    code = "FRESHNESS_PROFILE_NOT_FOUND"
    message = "소비기한 프로필을 찾을 수 없습니다."
    status_code = 422


async def list_ingredients(
    session: AsyncSession,
    *,
    user_id: int,
    page: int,
    size: int,
    storage_type: int | None = None,
    expiration_status: ExpirationStatus | None = None,
) -> Page[Ingredient]:
    """GET /ingredients — 소유·활성 목록."""
    offset = (page - 1) * size
    rows, total = await repository.list_active_by_user(
        session,
        user_id=user_id,
        storage_type=storage_type,
        expiration_status=expiration_status,
        offset=offset,
        limit=size,
    )
    items = [Ingredient.model_validate(row) for row in rows]
    return Page[Ingredient](items=items, page=page, size=size, total=total)


async def get_ingredient_detail(
    session: AsyncSession,
    *,
    user_id: int,
    ingredient_id: int,
) -> IngredientDetailResponse:
    """GET /ingredients/{id} — 상세(+ product/profile).

    직접입력(product_id/freshness_profile_id null)이면 해당 필드는 null로 남는다.
    """
    ingredient = await repository.get_owned_by_id(
        session, user_id=user_id, ingredient_id=ingredient_id
    )
    if ingredient is None:
        raise IngredientNotFoundError()

    product = None
    if ingredient.product_id is not None:
        product_row = await repository.get_product_by_id(
            session, product_id=ingredient.product_id
        )
        product = ProductRead.model_validate(product_row) if product_row else None

    freshness_profile = None
    if ingredient.freshness_profile_id is not None:
        profile_row = await repository.get_freshness_profile_by_id(
            session, freshness_profile_id=ingredient.freshness_profile_id
        )
        freshness_profile = (
            ProductFreshnessProfileRead.model_validate(profile_row) if profile_row else None
        )

    return IngredientDetailResponse(
        **Ingredient.model_validate(ingredient).model_dump(),
        product=product,
        freshness_profile=freshness_profile,
    )


async def create_ingredient(
    session: AsyncSession,
    *,
    user_id: int,
    data: IngredientCreateRequest,
) -> Ingredient:
    """POST /ingredients — 등록.

    직접입력(product_id/freshness_profile_id 생략)을 지원한다. 참조된 food/product/
    freshness_profile이 실제로 존재하는지 확인해 FK 위반으로 인한 500 대신 422로 응답한다.
    commit 경계는 이 함수에서 둔다.
    """
    if await repository.get_food_by_id(session, food_id=data.food_id) is None:
        raise FoodNotFoundError()

    if data.product_id is not None:
        if await repository.get_product_by_id(session, product_id=data.product_id) is None:
            raise ProductNotFoundError()

    profile = None
    if data.freshness_profile_id is not None:
        profile = await repository.get_freshness_profile_by_id(
            session, freshness_profile_id=data.freshness_profile_id
        )
        if profile is None:
            raise FreshnessProfileNotFoundError()

    expiration_date, expiration_status = _resolve_expiration(data, profile)

    ingredient = IngredientModel(
        user_id=user_id,
        food_id=data.food_id,
        product_id=data.product_id,
        freshness_profile_id=data.freshness_profile_id,
        name=data.name,
        storage_type=data.storage_type,
        quantity=data.quantity,
        unit=data.unit,
        purchase_date=data.purchase_date,
        expiration_date=expiration_date,
        expiration_source=data.expiration_source,
        expiration_status=expiration_status,
        image_url=data.image_url,
        memo=data.memo,
    )
    created = await repository.create(session, ingredient)
    await session.commit()
    await session.refresh(created)
    return Ingredient.model_validate(created)


def _resolve_expiration(
    data: IngredientCreateRequest,
    profile: ProductFreshnessProfile | None,
) -> tuple[date | None, ExpirationStatus]:
    """소비기한 규칙(노션 7항)을 현재 스키마가 가진 필드로 근사 적용한다.

    노션 규칙은 기준일 우선순위를 제조일→포장일→구매일→수령일→등록일로 두지만,
    이 스키마는 제조일/포장일/수령일을 별도로 받지 않는다(BE-1 정본 필드가 구매일까지만).
    그래서 실제 판단은 아래 두 갈래로 근사한다.

    - 사용자가 expiration_date를 직접 입력: 그 값을 그대로 확정으로 본다
      (포장지 등에서 실제 날짜를 읽어 입력한 경우이므로 CONFIRMED).
    - freshness_profile로 계산: 기준일(구매일, 없으면 등록일=오늘) + profile.expiration_days.
      "제조일 불명 + 제조일 기준 고시면 확정 금지" 판단은 데이터 파이프라인이 프로필을
      만들 때 이미 반영해 expiration_status로 내려주므로(BE-8 계약) 그대로 물려받는다.
    - 둘 다 없으면 확정할 근거가 없어 ESTIMATED.
    """
    if data.expiration_date is not None:
        return data.expiration_date, ExpirationStatus.CONFIRMED

    if profile is not None:
        base_date = data.purchase_date or date.today()
        expiration_date = base_date + timedelta(days=profile.expiration_days)
        return expiration_date, profile.expiration_status

    return None, ExpirationStatus.ESTIMATED


async def get_ingredient_summary(
    session: AsyncSession,
    *,
    user_id: int,
) -> IngredientSummaryResponse:
    """GET /ingredients/summary — 대시보드 집계.

    BE-5: 임박 D-day 상수 정의 + repository.summarize_active_by_user 매핑.
    """
    raise NotImplementedError("BE-5에서 구현")


async def recognize_ingredient_image(
    session: AsyncSession,
    *,
    user_id: int,
    image_bytes: bytes,
    filename: str | None = None,
) -> CameraRecognizeResponse:
    """POST /ingredients/recognitions — 카메라 후보(MVP fake).

    BE-7: fake adapter 주입. session은 후보 매칭용으로만 쓸 수 있음.
    """
    raise NotImplementedError("BE-7에서 구현")
