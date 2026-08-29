"""ingredients 업무 규칙과 transaction 경계.

DB는 repository에 위임하고, 여기서는 소유권·기본값·매핑 규칙을 담당한다.
실제 로직은 BE-3(목록·상세), BE-4(등록), BE-5(집계), BE-7(인식)에서 채운다.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import Page
from app.core.exceptions import AppError
from app.domains.freshness.enums import ExpirationStatus
from app.domains.ingredients import repository
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

    BE-4: 기본값(expiration_source/status)·ESTIMATED 규칙 적용 후 repository.create.
    commit 경계는 이 함수에서 둔다.
    """
    raise NotImplementedError("BE-4에서 구현")


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
