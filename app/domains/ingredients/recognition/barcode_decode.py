"""이미지에서 바코드 문자열을 디코딩한다."""

from __future__ import annotations

import logging
from io import BytesIO

logger = logging.getLogger(__name__)


def decode_barcodes(image_bytes: bytes) -> list[str]:
    """성공 시 바코드 값 목록(공백 제거). 실패/미검출이면 빈 리스트.

    pillow + pyzbar(+ libzbar)에 의존한다. 디코딩 실패를 예외로 올리지 않고
    빈 결과로 돌려, service가 '미인식'을 엉뚱한 추정으로 대체하지 않게 한다.
    """
    if not image_bytes:
        return []
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode as zbar_decode
    except ImportError:
        logger.warning("pyzbar/Pillow 미설치 — 바코드 디코딩 불가")
        return []

    try:
        image = Image.open(BytesIO(image_bytes))
        if image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")
        raw = zbar_decode(image)
    except Exception:
        logger.exception("바코드 디코딩 중 오류")
        return []

    codes: list[str] = []
    for item in raw:
        try:
            text = item.data.decode("utf-8", errors="ignore").strip().replace(" ", "")
        except Exception:
            continue
        if text and text not in codes:
            codes.append(text)
    return codes
