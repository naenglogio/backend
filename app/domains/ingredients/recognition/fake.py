"""카탈로그 기반 추정 adapter (MVP).

하드코딩 식품 목록을 쓰지 않는다. service가 넘긴 DB foods/products에서
이미지 바이트로 결정적으로 골라 confidence를 매긴다.
"""

from __future__ import annotations

import hashlib

from app.domains.ingredients.recognition.port import (
    CatalogFood,
    RecognitionCatalog,
    RecognitionHint,
    RecognizerPort,
)


def _strip_mock_prefix(name: str) -> str:
    prefix = "[MOCK] "
    return name[len(prefix) :] if name.startswith(prefix) else name


def _pivot(image_bytes: bytes, filename: str | None, size: int) -> int:
    """같은 이미지면 같은 후보가 나오도록 안정적인 시작 인덱스를 고른다."""
    if size <= 0:
        return 0
    material = image_bytes[:4096] + b"\0" + (filename or "").encode("utf-8", errors="ignore")
    digest = hashlib.sha256(material).digest()
    return int.from_bytes(digest[:4], "big") % size


def _confidences(count: int, *, start: float = 0.95, step: float = 0.07) -> list[float]:
    values: list[float] = []
    current = start
    for _ in range(count):
        values.append(round(max(0.5, min(0.99, current)), 2))
        current -= step
    return values


class CatalogPhotoRecognizer:
    """사진 인식 — 이미지 색 단서로 카탈로그 foods를 재순위한다.

    실비전 모델은 아니지만, 시금치(초록) 사진이 우유부터 나오는 식의
    이미지 무시 추정은 하지 않는다. 단서를 못 뽑으면 보수적으로 낮은
    confidence의 카탈로그 상위만 반환한다.
    """

    def __init__(self, *, take: int = 5) -> None:
        self._take = take

    async def recognize(
        self,
        *,
        image_bytes: bytes,
        filename: str | None = None,
        catalog: RecognitionCatalog,
    ) -> list[RecognitionHint]:
        from app.domains.ingredients.recognition.photo_features import (
            extract_image_cues,
            score_food_against_cues,
        )

        foods = list(catalog.foods)
        if not foods:
            return []

        cues = extract_image_cues(image_bytes)
        n = min(self._take, len(foods))

        if cues is None:
            # 이미지를 열 수 없으면 추정을 강하게 주장하지 않는다.
            start = _pivot(image_bytes, filename, len(foods))
            picked = [foods[(start + i) % len(foods)] for i in range(n)]
            scores = _confidences(n, start=0.58, step=0.03)
            return [
                RecognitionHint(
                    food_id=food.food_id,
                    name=food.food_name,
                    category_name=food.category_name,
                    confidence=score,
                )
                for food, score in zip(picked, scores, strict=True)
            ]

        ranked = sorted(
            foods,
            key=lambda f: score_food_against_cues(
                food_name=f.food_name,
                category_name=f.category_name,
                cues=cues,
            ),
            reverse=True,
        )
        picked = ranked[:n]
        raw_scores = [
            score_food_against_cues(
                food_name=f.food_name,
                category_name=f.category_name,
                cues=cues,
            )
            for f in picked
        ]
        top = max(raw_scores[0], 1e-6)
        # 최상위가 단서에 잘 맞으면 0.9대, 애매하면 더 낮게.
        peak = 0.92 if raw_scores[0] >= 0.15 else 0.72
        confidences = [
            round(max(0.5, min(0.95, peak * (s / top))), 2) for s in raw_scores
        ]
        # 동점이면 살짝 내림차순이 보이게 보정
        for i in range(1, len(confidences)):
            if confidences[i] >= confidences[i - 1]:
                confidences[i] = round(confidences[i - 1] - 0.03, 2)

        return [
            RecognitionHint(
                food_id=food.food_id,
                name=food.food_name,
                category_name=food.category_name,
                confidence=score,
            )
            for food, score in zip(picked, confidences, strict=True)
        ]


class CatalogBarcodeRecognizer:
    """바코드 — 이미지에서 코드를 읽고 products.external_id와 매칭한다.

    디코딩 실패 시 빈 목록(엉뚱한 상품 추정 금지).
    코드는 읽혔지만 카탈로그에 없으면 food_id=null 미등록 후보 1건.
    """

    async def recognize(
        self,
        *,
        image_bytes: bytes,
        filename: str | None = None,
        catalog: RecognitionCatalog,
    ) -> list[RecognitionHint]:
        _ = filename
        from app.domains.ingredients.recognition.barcode_decode import decode_barcodes

        codes = decode_barcodes(image_bytes)
        if not codes:
            return []

        code = codes[0]
        products = list(catalog.products)
        for product in products:
            if product.external_id == code:
                return [
                    RecognitionHint(
                        food_id=product.food_id,
                        name=_strip_mock_prefix(product.product_name) or product.food_name,
                        category_name=product.category_name,
                        confidence=0.98,
                    )
                ]

        return [
            RecognitionHint(
                food_id=None,
                name=f"미등록 상품 ({code})",
                category_name=None,
                confidence=0.55,
            )
        ]


class CatalogReceiptRecognizer:
    """영수증 — 카탈로그 foods에서 여러 라인 추정."""

    def __init__(self, *, take: int = 4) -> None:
        self._take = take

    async def recognize(
        self,
        *,
        image_bytes: bytes,
        filename: str | None = None,
        catalog: RecognitionCatalog,
    ) -> list[RecognitionHint]:
        foods = list(catalog.foods)
        if not foods:
            return []
        n = min(self._take, len(foods))
        start = _pivot(image_bytes, filename, len(foods))
        # 영수증은 서로 다른 라인처럼 보이게 간격을 두고 고른다.
        step = max(1, len(foods) // n)
        picked: list[CatalogFood] = []
        for i in range(n):
            picked.append(foods[(start + i * step) % len(foods)])
        scores = _confidences(n, start=0.91, step=0.06)
        return [
            RecognitionHint(
                food_id=food.food_id,
                name=food.food_name,
                category_name=food.category_name,
                confidence=score,
            )
            for food, score in zip(picked, scores, strict=True)
        ]


def build_fake_recognizer_registry() -> dict[str, RecognizerPort]:
    """모드 → 어댑터. 실모델 교체 시 이 레지스트리 항목만 갈아끼운다."""
    return {
        "photo": CatalogPhotoRecognizer(),
        "barcode": CatalogBarcodeRecognizer(),
        "receipt": CatalogReceiptRecognizer(),
    }


__all__ = [
    "CatalogBarcodeRecognizer",
    "CatalogPhotoRecognizer",
    "CatalogReceiptRecognizer",
    "build_fake_recognizer_registry",
]
