from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.router import api_router
from app.api.schemas import COMMON_ERROR_RESPONSES
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    # /health, /ready는 API 버전 프리픽스 없이 루트에 둔다.
    app.include_router(health_router, responses=COMMON_ERROR_RESPONSES)
    # 도메인 Router는 app/api/router.py에서 조립되어 API_PREFIX 아래에 연결된다.
    app.include_router(api_router, prefix=settings.API_PREFIX, responses=COMMON_ERROR_RESPONSES)

    return app


app = create_app()
