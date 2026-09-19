"""DINOv2-small ONNX 임베딩 — 사진 인식(photo 모드)의 벡터 인코더.

쿼리 시점(사용자 업로드 사진)과 파이프라인의 갤러리 인코딩(crowling_ocr_parser)이
반드시 똑같은 전처리·모델을 써야 같은 벡터 공간에서 비교할 수 있다. 여기서 바뀌면
파이프라인 쪽 인코더도 같이 바꿔야 한다 — model_version 문자열로 서로 다른 버전이
섞이지 않게 막는다(product_image_embeddings.model_version).

PyTorch/transformers는 여기서 필요 없다 — onnxruntime만으로 추론한다(이미지 빌드를
가볍게 유지하기 위함). 모델 파일(dinov2_small_pooled.onnx(.data))은 PyTorch로
`facebook/dinov2-small`을 pooler_output까지 포함해 1회 export한 결과물이다.
community에 올라온 기본 ONNX export는 last_hidden_state만 내놓고 최종 LayerNorm이
빠져 있어(검증 중 실측으로 확인 — CLS 토큰을 직접 꺼내면 같은 상품 사진끼리도
유사도가 거의 0으로 나옴), pooler_output을 명시적으로 그래프에 넣어 재export했다.
"""

from __future__ import annotations

import os
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL_VERSION = "dinov2-small-pooled-onnx-v1"
EMBEDDING_DIM = 384

_MODEL_PATH = Path(
    os.environ.get("IMAGE_EMBEDDING_MODEL_PATH", "var/models/dinov2_small_pooled.onnx")
)

# onnx-community/dinov2-small의 preprocessor_config.json과 동일해야 한다.
_RESIZE_SHORTEST_EDGE = 256
_CROP_SIZE = 224
_IMAGE_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_IMAGE_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


class EmbeddingModelUnavailableError(RuntimeError):
    """ONNX 모델 파일을 못 찾았을 때. 인식 요청을 500으로 실패시키되 원인을 명확히 한다."""


@lru_cache(maxsize=1)
def _session() -> ort.InferenceSession:
    if not _MODEL_PATH.is_file():
        raise EmbeddingModelUnavailableError(f"ONNX model not found: {_MODEL_PATH}")
    so = ort.SessionOptions()
    so.intra_op_num_threads = 1
    so.inter_op_num_threads = 1
    return ort.InferenceSession(
        str(_MODEL_PATH), sess_options=so, providers=["CPUExecutionProvider"]
    )


def _resize_shortest_edge(image: Image.Image, size: int) -> Image.Image:
    w, h = image.size
    if w <= h:
        new_w, new_h = size, round(size * h / w)
    else:
        new_w, new_h = round(size * w / h), size
    return image.resize((new_w, new_h), resample=Image.Resampling.BICUBIC)


def _center_crop(image: Image.Image, size: int) -> Image.Image:
    w, h = image.size
    left = (w - size) // 2
    top = (h - size) // 2
    return image.crop((left, top, left + size, top + size))


def preprocess(image_bytes: bytes) -> np.ndarray:
    """이미지 바이트 -> (1, 3, 224, 224) float32 NCHW. BitImageProcessor 설정과 동일."""
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image = _resize_shortest_edge(image, _RESIZE_SHORTEST_EDGE)
    image = _center_crop(image, _CROP_SIZE)
    array = np.asarray(image, dtype=np.float32) / 255.0
    array = (array - _IMAGE_MEAN) / _IMAGE_STD
    array = array.transpose(2, 0, 1)  # HWC -> CHW
    return np.expand_dims(array, axis=0)


def embed_image(image_bytes: bytes) -> list[float]:
    """이미지 -> L2 정규화된 384차원 임베딩. 코사인 유사도는 내적으로 바로 계산 가능."""
    pixel_values = preprocess(image_bytes)
    outputs = _session().run(["pooled_output"], {"pixel_values": pixel_values})
    pooled = outputs[0][0]
    norm = np.linalg.norm(pooled)
    if norm > 0:
        pooled = pooled / norm
    return pooled.astype(np.float32).tolist()
