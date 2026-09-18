"""스캔 인식 포트 (BE-7).

실모델/OCR/바코드 엔진은 이 인터페이스 뒤에만 둔다.
service/router는 RecognizerPort만 알면 되고, MVP는 fake adapter를 주입한다.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class RecognitionMode(StrEnum):
    PHOTO = "photo"
    BARCODE = "barcode"
    RECEIPT = "receipt"


@dataclass(frozen=True, slots=True)
class RecognitionHint:
    """어댑터가 돌려주는 원시 후보. food_id 매칭은 service가 한다."""

    food_name: str
    category_name: str | None
    confidence: float


class RecognizerPort(Protocol):
    async def recognize(
        self,
        *,
        image_bytes: bytes,
        filename: str | None = None,
    ) -> list[RecognitionHint]:
        """이미지 바이트를 받아 후보 힌트 목록을 반환한다.

        구현체는 이미지를 실제로 쓰지 않아도 된다(fake).
        confidence는 0~1 범위로 맞춘다. 정렬은 service가 다시 한다.
        """
        ...
