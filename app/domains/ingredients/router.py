"""ingredients HTTP 입출력.

BE-2 #04: 계약서 경로를 Swagger에 노출하고 service로만 위임한다.
ORM 금지. 실제 동작은 BE-3~7에서 service/repository를 채운 뒤 살아난다.

경로 순서 주의: /summary, /recognitions 를 /{ingredient_id} 보다 먼저 둔다.
"""

from typing import Annotated, Literal

from fastapi import APIRouter, File, Query, UploadFile, status

from app.api.dependencies import CurrentUserId, DBSession, PageQuery
from app.api.schemas import COMMON_ERROR_RESPONSES, Page
from app.domains.freshness.enums import ExpirationStatus
from app.domains.ingredients.schema import (
    CameraRecognizeResponse,
    Ingredient,
    IngredientCreateRequest,
    IngredientDetailResponse,
    IngredientSummaryResponse,
)
from app.domains.ingredients.service import (
    create_ingredient,
    get_ingredient_detail,
    get_ingredient_summary,
    list_ingredients,
    recognize_ingredient_image,
)

router = APIRouter()


@router.get(
    "",
    response_model=Page[Ingredient],
    responses={401: {"description": "인증 필요"}, **COMMON_ERROR_RESPONSES},
)
async def get_ingredients(
    session: DBSession,
    user_id: CurrentUserId,
    page_query: PageQuery,
    storage_type: Annotated[Literal[0, 1] | None, Query()] = None,
    expiration_status: Annotated[ExpirationStatus | None, Query()] = None,
) -> Page[Ingredient]:
    """목록 조회. BE-3에서 구현."""
    return await list_ingredients(
        session,
        user_id=user_id,
        page=page_query.page,
        size=page_query.size,
        storage_type=storage_type,
        expiration_status=expiration_status,
    )


@router.get(
    "/summary",
    response_model=IngredientSummaryResponse,
    responses={401: {"description": "인증 필요"}, **COMMON_ERROR_RESPONSES},
)
async def get_summary(
    session: DBSession,
    user_id: CurrentUserId,
) -> IngredientSummaryResponse:
    """대시보드 집계. BE-5에서 구현."""
    return await get_ingredient_summary(session, user_id=user_id)


@router.post(
    "/recognitions",
    response_model=CameraRecognizeResponse,
    responses={
        401: {"description": "인증 필요"},
        400: {"description": "이미지 누락 등"},
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_recognition(
    session: DBSession,
    user_id: CurrentUserId,
    image: Annotated[UploadFile, File(description="식재료 사진")],
) -> CameraRecognizeResponse:
    """카메라 인식 후보. BE-7에서 fake adapter 구현."""
    image_bytes = await image.read()
    return await recognize_ingredient_image(
        session,
        user_id=user_id,
        image_bytes=image_bytes,
        filename=image.filename,
    )


@router.get(
    "/{ingredient_id}",
    response_model=IngredientDetailResponse,
    responses={
        401: {"description": "인증 필요"},
        404: {"description": "없거나 남의 식재료"},
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_ingredient(
    ingredient_id: int,
    session: DBSession,
    user_id: CurrentUserId,
) -> IngredientDetailResponse:
    """상세 조회. BE-3에서 구현."""
    return await get_ingredient_detail(
        session,
        user_id=user_id,
        ingredient_id=ingredient_id,
    )


@router.post(
    "",
    response_model=Ingredient,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"description": "인증 필요"},
        422: {"description": "요청 값 검증 실패"},
        **COMMON_ERROR_RESPONSES,
    },
)
async def post_ingredient(
    data: IngredientCreateRequest,
    session: DBSession,
    user_id: CurrentUserId,
) -> Ingredient:
    """식재료 등록. BE-4에서 구현."""
    return await create_ingredient(session, user_id=user_id, data=data)
