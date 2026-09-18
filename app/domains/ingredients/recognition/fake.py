"""MVP fake adapters. 실제 추론 없이 seed foods와 맞는 목업 후보를 반환한다."""

from app.domains.ingredients.recognition.port import RecognitionHint, RecognizerPort


class FakePhotoRecognizer:
    """식재료 사진 인식 fake — 후보 3~5개."""

    async def recognize(
        self,
        *,
        image_bytes: bytes,
        filename: str | None = None,
    ) -> list[RecognitionHint]:
        _ = (image_bytes, filename)
        return [
            RecognitionHint("우유", "유제품", 0.94),
            RecognitionHint("고등어", "해산물", 0.87),
            RecognitionHint("계란", "유제품", 0.81),
            RecognitionHint("양파", "채소", 0.72),
            RecognitionHint("당근", "채소", 0.65),
        ]


class FakeBarcodeRecognizer:
    """바코드 스캔 fake — 상품 1건."""

    async def recognize(
        self,
        *,
        image_bytes: bytes,
        filename: str | None = None,
    ) -> list[RecognitionHint]:
        _ = (image_bytes, filename)
        return [RecognitionHint("우유", "유제품", 0.99)]


class FakeReceiptRecognizer:
    """영수증 OCR fake — 라인별 여러 건."""

    async def recognize(
        self,
        *,
        image_bytes: bytes,
        filename: str | None = None,
    ) -> list[RecognitionHint]:
        _ = (image_bytes, filename)
        return [
            RecognitionHint("우유", "유제품", 0.91),
            RecognitionHint("계란", "유제품", 0.88),
            RecognitionHint("시금치", "채소", 0.76),
            RecognitionHint("냉동만두", "가공식품", 0.70),
        ]


def build_fake_recognizer_registry() -> dict[str, RecognizerPort]:
    """모드 → 어댑터. 실모델 교체 시 이 레지스트리 항목만 갈아끼운다."""
    return {
        "photo": FakePhotoRecognizer(),
        "barcode": FakeBarcodeRecognizer(),
        "receipt": FakeReceiptRecognizer(),
    }
