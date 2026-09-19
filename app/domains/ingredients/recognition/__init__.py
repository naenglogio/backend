"""인식 하위 패키지. service는 RecognizerPort만 의존한다."""

from app.domains.ingredients.recognition.embedding_recognizer import EmbeddingPhotoRecognizer
from app.domains.ingredients.recognition.fake import CatalogReceiptRecognizer
from app.domains.ingredients.recognition.port import (
    CatalogFood,
    CatalogProduct,
    CatalogProductImage,
    RecognitionCatalog,
    RecognitionHint,
    RecognitionMode,
    RecognizerPort,
)


def build_recognizer_registry() -> dict[str, RecognizerPort]:
    """모드 -> adapter. photo는 임베딩 검색(실모델), receipt는 아직 fake."""
    return {
        "photo": EmbeddingPhotoRecognizer(),
        "receipt": CatalogReceiptRecognizer(),
    }


__all__ = [
    "CatalogFood",
    "CatalogProduct",
    "CatalogProductImage",
    "RecognitionCatalog",
    "RecognitionHint",
    "RecognitionMode",
    "RecognizerPort",
    "build_recognizer_registry",
]
