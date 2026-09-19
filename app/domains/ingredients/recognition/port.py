"""스캔 인식 포트 (BE-7).

실모델/OCR 엔진은 이 인터페이스 뒤에만 둔다.
MVP는 DB 카탈로그(실제 foods/products)를 보고 후보를 추정하는 adapter를 쓴다.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class RecognitionMode(StrEnum):
    PHOTO = "photo"
    RECEIPT = "receipt"


@dataclass(frozen=True, slots=True)
class CatalogFood:
    """인식에 쓰는 식품 마스터 스냅샷."""

    food_id: int
    food_name: str
    category_name: str | None


@dataclass(frozen=True, slots=True)
class CatalogProduct:
    """인식에 쓰는 상품 스냅샷."""

    product_id: int
    external_id: str
    product_name: str
    food_id: int
    food_name: str
    category_name: str | None


@dataclass(frozen=True, slots=True)
class CatalogProductImage:
    """사진 인식(임베딩 검색)의 갤러리 항목 — 상품 이미지 1장의 시각 임베딩."""

    external_id: str
    product_name: str
    embedding: Sequence[float]
    food_id: int
    food_name: str
    category_name: str | None


@dataclass(frozen=True, slots=True)
class RecognitionCatalog:
    foods: Sequence[CatalogFood]
    products: Sequence[CatalogProduct]
    # photo 모드에서만 채운다 — 다른 모드는 안 쓰는데 매 요청 DB에서 끌어오면 낭비라서.
    product_images: Sequence[CatalogProductImage] = ()


@dataclass(frozen=True, slots=True)
class RecognitionHint:
    """어댑터가 돌려주는 후보. 이미 DB 실데이터를 가리킨다."""

    food_id: int | None
    name: str
    category_name: str | None
    confidence: float


class RecognizerPort(Protocol):
    async def recognize(
        self,
        *,
        image_bytes: bytes,
        filename: str | None = None,
        catalog: RecognitionCatalog,
    ) -> list[RecognitionHint]:
        """이미지 + 카탈로그로 후보를 추정한다.

        MVP 구현은 이미지를 추론하지 않고, 바이트/파일명으로 카탈로그에서
        결정적으로 고른다. 실모델 교체 시 같은 시그니처를 유지한다.
        """
        ...
