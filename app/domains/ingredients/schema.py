"""ingredients 도메인 Pydantic 요청·응답 계약.

BE-2 첫 슬라이스: shared/00_API_CONTRACT.md 와 1:1로 맞춘다.
실제 HTTP 엔드포인트·DB 로직은 BE-3~7에서 채운다.
ORM 컬럼을 그대로 노출하지 않고, API에 필요한 필드만 정의한다.
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domains.freshness.enums import ExpirationSource, ExpirationStatus, StorageType
from app.domains.ingredients.enums import DeletionReason
from app.domains.products.enums import ProductSource


# ingredients.storage_type 정본: 0=냉장, 1=냉동
StorageTypeInt = Literal[0, 1]


class Ingredient(BaseModel):
    """목록·등록 응답의 식재료 본문. 계약서 Ingredient와 동일."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    food_id: int
    product_id: int | None
    freshness_profile_id: int | None
    name: str
    storage_type: StorageTypeInt
    quantity: int
    unit: str | None
    purchase_date: date | None
    expiration_date: date | None
    expiration_source: ExpirationSource
    expiration_status: ExpirationStatus
    is_deleted: bool
    deletion_reason: DeletionReason | None
    image_url: str | None
    memo: str | None
    created_at: datetime
    updated_at: datetime | None


class IngredientCreateRequest(BaseModel):
    """POST /ingredients 요청 본문."""

    food_id: int
    product_id: int | None = None
    freshness_profile_id: int | None = None
    name: str = Field(min_length=1, max_length=255)
    storage_type: StorageTypeInt
    quantity: int = Field(gt=0)
    unit: str | None = Field(default=None, max_length=30)
    purchase_date: date | None = None
    expiration_date: date | None = None
    # 미지정 시 서비스에서 USER_INPUT로 채운다.
    expiration_source: ExpirationSource = ExpirationSource.USER_INPUT
    image_url: str | None = None
    memo: str | None = None


class ProductRead(BaseModel):
    """상세 응답에 붙는 상품 요약. 직접 입력이면 null."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    food_id: int
    source: ProductSource
    external_id: str
    name: str
    created_at: datetime
    updated_at: datetime | None


class ProductFreshnessProfileRead(BaseModel):
    """상세 응답에 붙는 소비기한 프로필. 직접 입력이면 null.

    프로필 테이블의 storage_type은 아직 문자열 enum(StorageType)이다.
    ingredients.storage_type(int)과 다르다.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    food_id: int
    product_id: int | None
    storage_type: StorageType
    expiration_days: int
    expiration_source: ExpirationSource
    expiration_status: ExpirationStatus
    created_at: datetime
    updated_at: datetime | None


class IngredientDetailResponse(Ingredient):
    """GET /ingredients/{id} 응답 = Ingredient + 연관 product/profile."""

    product: ProductRead | None = None
    freshness_profile: ProductFreshnessProfileRead | None = None


class RecognitionCandidate(BaseModel):
    """카메라 인식 후보 1건. 등록 화면 프리필에 사용."""

    food_id: int | None
    name: str
    category: str | None
    confidence: float = Field(ge=0, le=1)


class CameraRecognizeResponse(BaseModel):
    """POST /ingredients/recognitions 응답."""

    candidates: list[RecognitionCandidate]


class ExpiringItem(BaseModel):
    """대시보드 임박 목록 항목."""

    id: int
    name: str
    storage_type: StorageTypeInt
    expiration_date: date | None


class IngredientSummaryResponse(BaseModel):
    """GET /ingredients/summary 응답."""

    total: int
    refrigerated_count: int
    frozen_count: int
    expiring_count: int
    expiring_items: list[ExpiringItem]
