import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.db.session import engine

logger = logging.getLogger(__name__)

# 인프라 상태 확인용 엔드포인트. API_PREFIX 밖(루트)에 둬서 오케스트레이터/헬스체크가
# 버전 프리픽스와 무관하게 호출할 수 있게 한다.
router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """프로세스 생존 확인. 외부 의존성(DB 등)은 확인하지 않는다."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check() -> JSONResponse:
    """DB 연결 준비 여부를 확인한다. 연결 실패 시 503을 반환한다."""
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Readiness check failed: database not reachable")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready"},
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ready"})
