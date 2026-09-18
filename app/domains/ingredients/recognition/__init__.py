"""인식 하위 패키지. service는 RecognizerPort만 의존한다."""

from app.domains.ingredients.recognition.fake import build_fake_recognizer_registry
from app.domains.ingredients.recognition.port import (
    RecognitionHint,
    RecognitionMode,
    RecognizerPort,
)

__all__ = [
    "RecognitionHint",
    "RecognitionMode",
    "RecognizerPort",
    "build_fake_recognizer_registry",
]
