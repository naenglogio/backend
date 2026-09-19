from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import IDMixin, TimestampMixin
from app.domains.products.enums import ProductSource

# DINOv2-small pooled 출력 차원. embedding_model.py의 모델을 바꾸면 이 값과
# 마이그레이션의 vector(...) 차원도 같이 바꿔야 한다.
IMAGE_EMBEDDING_DIM = 384


class Product(IDMixin, TimestampMixin, Base):
    """컬리N마트 상품 식별.

    가격은 서비스 요구사항이 아니므로 컬럼을 두지 않는다.
    """

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_products_source_external_id"),
    )

    food_id: Mapped[int] = mapped_column(
        ForeignKey("foods.id", ondelete="RESTRICT"), nullable=False
    )
    source: Mapped[ProductSource] = mapped_column(
        SAEnum(
            ProductSource,
            name="source",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)


class ProductImageEmbedding(IDMixin, TimestampMixin, Base):
    """상품 이미지 1장의 시각 임베딩 — 사진 인식(BE-7 photo 모드)의 검색 대상 갤러리.

    데이터 파이프라인(crowling_ocr_parser)이 크롤링한 상품 상세 이미지를 DINOv2로
    인코딩해 넘긴 값을 그대로 저장한다. 원본 이미지는 여기 저장하지 않는다(파이프라인
    책임). model_version이 다르면 같은 벡터 공간이 아니므로 검색 시 반드시 필터링한다.
    """

    __tablename__ = "product_image_embeddings"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "image_hash", "model_version", name="uq_product_image_embeddings"
        ),
        Index(
            "ix_product_image_embeddings_embedding_cosine",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    image_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(IMAGE_EMBEDDING_DIM), nullable=False)
    model_version: Mapped[str] = mapped_column(Text, nullable=False)
