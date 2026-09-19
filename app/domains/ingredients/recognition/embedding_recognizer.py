"""사진 인식(photo 모드) — DINOv2 임베딩 최근접 이웃 검색.

색상 휴리스틱(photo_features.py)의 후속. 실사진 검증 결과(대화 기록 참고) 정확도가
낮아 "자동 확정"으로는 못 쓰고, 후보 3~5개를 순위대로 반환해 프론트가 사용자
확인 UI로 최종 선택하게 하는 용도로만 쓴다 — 이 adapter는 그 후보 목록만 만든다.
"""

from __future__ import annotations

import logging

import numpy as np

from app.domains.ingredients.recognition.embedding_model import (
    EmbeddingModelUnavailableError,
    embed_image,
)
from app.domains.ingredients.recognition.port import RecognitionCatalog, RecognitionHint

logger = logging.getLogger(__name__)

_TOP_K = 5


class EmbeddingPhotoRecognizer:
    """product_image_embeddings 갤러리에서 코사인 유사도 최근접 이웃을 찾는다."""

    async def recognize(
        self,
        *,
        image_bytes: bytes,
        filename: str | None = None,
        catalog: RecognitionCatalog,
    ) -> list[RecognitionHint]:
        _ = filename
        gallery = catalog.product_images
        if not gallery:
            return []

        try:
            query_vec = np.array(embed_image(image_bytes), dtype=np.float32)
        except EmbeddingModelUnavailableError:
            logger.exception("Embedding model unavailable — photo recognition degraded to empty")
            return []

        scored = [
            (float(np.dot(query_vec, np.array(item.embedding, dtype=np.float32))), item)
            for item in gallery
        ]
        scored.sort(key=lambda pair: -pair[0])

        seen_foods: set[int] = set()
        hints: list[RecognitionHint] = []
        for score, item in scored:
            if item.food_id in seen_foods:
                continue
            seen_foods.add(item.food_id)
            hints.append(
                RecognitionHint(
                    food_id=item.food_id,
                    name=item.food_name,
                    category_name=item.category_name,
                    # 코사인 유사도를 그대로 confidence로 쓴다. 실사진에서는 최고
                    # 매치도 0.3~0.5대로 낮게 나올 수 있다 — 자동 확정이 아니라
                    # 순위 참고용이라는 걸 프론트/사용자에게 그대로 보여준다.
                    confidence=max(0.0, min(1.0, score)),
                )
            )
            if len(hints) >= _TOP_K:
                break
        return hints
