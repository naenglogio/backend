"""ingredients DB 질의 계층.

BE-2 #02: Router/Service가 호출할 메서드 자리만 둔다.
실제 쿼리 구현은 BE-3(목록·상세), BE-4(등록), BE-5(집계)에서 채운다.
ORM은 이 모듈에서만 사용한다 (router 금지).
"""

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

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

    BE-3: 필터(optional)·페이지네이션 쿼리 구현.
    """
    raise NotImplementedError("BE-3에서 구현")


async def get_owned_by_id(
    session: AsyncSession,
    *,
    user_id: int,
    ingredient_id: int,
) -> Ingredient | None:
    """본인 소유 ingredient 단건. 없거나 남의 것이면 None → service에서 404.

    BE-3: 소유권 조건 조회 구현.
    """
    raise NotImplementedError("BE-3에서 구현")


async def get_product_by_id(
    session: AsyncSession,
    *,
    product_id: int,
) -> Product | None:
    """상세 응답 nested product용.

    BE-3: product_id로 Product 조회.
    """
    raise NotImplementedError("BE-3에서 구현")


async def get_freshness_profile_by_id(
    session: AsyncSession,
    *,
    freshness_profile_id: int,
) -> ProductFreshnessProfile | None:
    """상세 응답 nested freshness_profile용.

    BE-3: freshness_profile_id로 ProductFreshnessProfile 조회.
    """
    raise NotImplementedError("BE-3에서 구현")


async def create(
    session: AsyncSession,
    ingredient: Ingredient,
) -> Ingredient:
    """식재료 행 추가 후 flush/refresh한 엔티티 반환.

    BE-4: session.add + commit 경계는 service가 담당할지 여기서 할지 결정 후 구현.
    """
    raise NotImplementedError("BE-4에서 구현")


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
