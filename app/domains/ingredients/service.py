"""ingredients 업무 규칙과 transaction 경계.

DB는 repository에 위임하고, 여기서는 소유권·기본값·매핑 규칙을 담당한다.
실제 로직은 BE-3(목록·상세), BE-4(등록), BE-5(집계), BE-7(인식)에서 채운다.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import Page
from app.core.exceptions import AppError
from app.domains.freshness.enums import ExpirationStatus
from app.domains.freshness.model import ProductFreshnessProfile
from app.domains.ingredients import repository
from app.domains.ingredients.model import Ingredient as IngredientModel
from app.domains.ingredients.recognition import (
    CatalogFood,
    CatalogProduct,
    RecognitionCatalog,
    RecognitionMode,
    RecognizerPort,
    build_fake_recognizer_registry,
)
from app.domains.ingredients.schema import (
    CameraRecognizeResponse,
    Ingredient,
    IngredientCreateRequest,
    IngredientDetailResponse,
    IngredientSummaryResponse,
    ProductFreshnessProfileRead,
    ProductRead,
    RecognitionCandidate,
)

# MVP: fake 레지스트리. 실모델 도입 시 이 한곳만 교체하면 router/service 계약은 그대로다.
_RECOGNIZERS: dict[str, RecognizerPort] = build_fake_recognizer_registry()


# 임박(D-day) 기준. 대시보드 카운트와 프론트 임박 배지가 같은 값을 봐야 하므로 상수로 고정한다.
# expiration_date가 오늘부터 3일 이내면 임박이고, 이미 지난 항목도 임박에 포함한다.
EXPIRING_WITHIN_DAYS = 3
# 임박 카드에 노출할 최대 건수. 전체 임박 개수는 expiring_count로 따로 내려간다.
EXPIRING_ITEMS_TOP_N = 5

# 컨테이너 TZ가 UTC라 date.today()를 쓰면 KST 00~09시에 하루 전 날짜가 나와 D-day가
# 하루 밀린다. 소비기한은 사용자가 보는 날짜 기준이어야 하므로 KST로 계산한다.
# 한국은 DST가 없어 고정 오프셋으로 충분하다.
_KST = timezone(timedelta(hours=9))


def today_in_service_tz() -> date:
    """소비기한 계산·임박 판정의 기준이 되는 '오늘'(KST)."""
    return datetime.now(_KST).date()


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


class ImageMissingError(AppError):
    """인식 요청에 이미지 바이트가 없을 때."""

    code = "IMAGE_MISSING"
    message = "인식할 이미지가 필요합니다."
    status_code = 400


class UnsupportedRecognitionModeError(AppError):
    """지원하지 않는 mode 값."""

    code = "UNSUPPORTED_RECOGNITION_MODE"
    message = "지원하지 않는 인식 모드입니다."
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
        product_row = await repository.get_product_by_id(session, product_id=ingredient.product_id)
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
        base_date = data.purchase_date or today_in_service_tz()
        expiration_date = base_date + timedelta(days=profile.expiration_days)
        return expiration_date, profile.expiration_status

    return None, ExpirationStatus.ESTIMATED


async def get_ingredient_summary(
    session: AsyncSession,
    *,
    user_id: int,
) -> IngredientSummaryResponse:
    """GET /ingredients/summary — 대시보드 집계.

    임박 판정 기준일은 사용자가 화면에서 보는 날짜여야 하므로 KST 기준 오늘을 쓴다.
    """
    raw = await repository.summarize_active_by_user(
        session,
        user_id=user_id,
        today=today_in_service_tz(),
        expiring_within_days=EXPIRING_WITHIN_DAYS,
        expiring_top_n=EXPIRING_ITEMS_TOP_N,
    )
    return IngredientSummaryResponse.model_validate(raw)


async def recognize_ingredient_image(
    session: AsyncSession,
    *,
    user_id: int,
    image_bytes: bytes,
    filename: str | None = None,
    mode: RecognitionMode = RecognitionMode.PHOTO,
    recognizer: RecognizerPort | None = None,
) -> CameraRecognizeResponse:
    """POST /ingredients/recognitions — 스캔 후보 추정.

    MVP는 실추론 대신 DB 카탈로그(foods/products)에서 이미지 바이트 기준으로
    결정적으로 고른다. user_id는 인증 경계 확인용.
    """
    _ = user_id
    if not image_bytes:
        raise ImageMissingError()

    adapter = recognizer or _RECOGNIZERS.get(mode.value)
    if adapter is None:
        raise UnsupportedRecognitionModeError(details={"mode": mode.value})

    food_rows, product_rows = await repository.list_recognition_catalog(session)
    catalog = RecognitionCatalog(
        foods=[
            CatalogFood(food_id=fid, food_name=fname, category_name=cat)
            for fid, fname, cat in food_rows
        ],
        products=[
            CatalogProduct(
                product_id=pid,
                external_id=ext,
                product_name=pname,
                food_id=fid,
                food_name=fname,
                category_name=cat,
            )
            for pid, ext, pname, fid, fname, cat in product_rows
        ],
    )

    hints = await adapter.recognize(image_bytes=image_bytes, filename=filename, catalog=catalog)
    candidates = [
        RecognitionCandidate(
            food_id=hint.food_id,
            name=hint.name,
            category=hint.category_name,
            confidence=hint.confidence,
        )
        for hint in hints
    ]
    candidates.sort(key=lambda c: c.confidence, reverse=True)
    return CameraRecognizeResponse(candidates=candidates)
