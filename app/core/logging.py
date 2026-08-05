import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings


class JSONLogFormatter(logging.Formatter):
    """모든 애플리케이션 로그를 한 줄짜리 JSON으로 남긴다."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    """애플리케이션 전역 로깅을 설정한다. 앱 시작 시 한 번만 호출한다."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONLogFormatter())

    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # uvicorn 자체 로거도 동일한 포맷을 쓰도록 핸들러를 통일한다.
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True
