"""사진 인식용 단순 시각 단서(색 분포).

실비전 모델이 없을 때, 이미지 픽셀로 카탈로그 후보를 재순위한다.
배경(흰/검은 여백)은 빼고 '내용 픽셀'만 본다 — 시금치 사진이 유제품으로
나오는 일을 줄이기 위한 MVP 추정이다.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ImageCues:
    green: float
    orange: float
    red: float
    yellow: float
    white: float
    brown: float
    pink: float


_FOOD_WEIGHTS: dict[str, dict[str, float]] = {
    "시금치": {"green": 4.0},
    "당근": {"orange": 4.0},
    "양파": {"brown": 1.8, "white": 1.0, "yellow": 0.4},
    "우유": {"white": 3.0},
    "요거트": {"white": 2.6, "yellow": 0.3},
    "계란": {"white": 1.6, "yellow": 2.2},
    "즉석밥": {"white": 0.8, "brown": 0.6},
    "냉동만두": {"brown": 1.0, "yellow": 0.8, "white": 0.4},
    "닭가슴살": {"pink": 2.2, "white": 1.0},
    "돼지고기": {"pink": 2.5, "red": 1.2},
    "고등어": {"brown": 0.6, "white": 0.5},
    "새우": {"pink": 2.8, "orange": 1.5},
    "과자": {"yellow": 1.8, "brown": 1.2, "orange": 0.6},
}

_CATEGORY_WEIGHTS: dict[str, dict[str, float]] = {
    "채소": {"green": 1.6, "orange": 1.0, "brown": 0.4},
    "유제품": {"white": 1.8, "yellow": 0.5},
    "육류": {"pink": 1.6, "red": 1.2, "brown": 0.6},
    "해산물": {"pink": 1.0, "white": 0.4},
    "과자": {"yellow": 1.0, "brown": 0.8},
    "가공식품": {"brown": 0.4, "yellow": 0.3, "white": 0.3},
}


def _is_background(r: int, g: int, b: int) -> bool:
    """UI/여백으로 보이는 극단 밝기·어두운 픽셀은 제외한다."""
    if r > 230 and g > 230 and b > 230:
        return True
    if r < 20 and g < 20 and b < 20:
        return True
    # 파란 버튼 등 UI 악센트도 음식 단서에서 제외
    if b > r + 40 and b > g + 40 and b > 120:
        return True
    return False


def extract_image_cues(image_bytes: bytes) -> ImageCues | None:
    """내용 픽셀 기준 색 단서(0~1). 열 수 없거나 내용이 없으면 None."""
    if not image_bytes:
        return None
    try:
        from PIL import Image
    except ImportError:
        logger.warning("Pillow 미설치 — 사진 색 단서 추출 불가")
        return None

    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        # 중앙·상단(카메라 프리뷰)을 조금 더 보도록 크롭 후 축소
        w, h = image.size
        image = image.crop((int(w * 0.08), int(h * 0.05), int(w * 0.92), int(h * 0.62)))
        image = image.resize((96, 96))
        pixels = list(image.getdata())
    except Exception:
        logger.exception("사진 색 단서 추출 실패")
        return None

    content = [(r, g, b) for r, g, b in pixels if not _is_background(r, g, b)]
    if len(content) < 30:
        # 내용이 거의 없으면 전체 픽셀로 폴백
        content = list(pixels)
    if not content:
        return None

    n = float(len(content))
    green = orange = red = yellow = white = brown = pink = 0.0

    for r, g, b in content:
        if g > r + 15 and g > b + 10 and g > 50:
            green += 1.0
        if r > 140 and 60 < g < 180 and b < 110 and r > g > b:
            orange += 1.0
        if r > 130 and r > g + 40 and r > b + 40:
            red += 1.0
        if r > 150 and g > 140 and b < 120 and abs(r - g) < 55:
            yellow += 1.0
        # 내용 영역 안의 '흰 식품'(우유 등) — 배경 임계보다 낮게
        if r > 175 and g > 175 and b > 175 and (max(r, g, b) - min(r, g, b)) < 40:
            white += 1.0
        if 70 < r < 170 and 40 < g < 130 and b < 100 and r >= g >= b:
            brown += 1.0
        if r > 140 and 80 < g < 170 and 80 < b < 170 and r > g and abs(g - b) < 40:
            pink += 1.0

    return ImageCues(
        green=green / n,
        orange=orange / n,
        red=red / n,
        yellow=yellow / n,
        white=white / n,
        brown=brown / n,
        pink=pink / n,
    )


def score_food_against_cues(
    *,
    food_name: str,
    category_name: str | None,
    cues: ImageCues,
) -> float:
    cue_map = {
        "green": cues.green,
        "orange": cues.orange,
        "red": cues.red,
        "yellow": cues.yellow,
        "white": cues.white,
        "brown": cues.brown,
        "pink": cues.pink,
    }
    score = 0.0
    for key, weight in _FOOD_WEIGHTS.get(food_name, {}).items():
        score += weight * cue_map.get(key, 0.0)
    if category_name:
        for key, weight in _CATEGORY_WEIGHTS.get(category_name, {}).items():
            score += weight * cue_map.get(key, 0.0)
    # 초록이 뚜렷하면 유제품(white) 가산을 눌러 시금치 오인식을 줄인다.
    if cues.green >= 0.12 and food_name in {"우유", "요거트", "계란"}:
        score *= 0.35
    return score
