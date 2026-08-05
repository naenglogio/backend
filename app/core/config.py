from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "NaengLog API"
    APP_ENV: Literal["local", "test", "development", "production"] = "local"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    # 로컬 기본값은 단순하게 두고, 운영 튜닝이 필요해지면 환경변수로 조절한다.
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    LOG_LEVEL: str = "INFO"

    # 콤마로 구분된 문자열(.env)을 안전하게 리스트로 변환한다.
    # 운영 환경 wildcard("*")를 기본값으로 두지 않고, 로컬 프런트엔드 origin만 기본 허용한다.
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


# 대부분의 코드는 모듈 임포트 시점에 확정된 단일 설정 객체를 사용한다.
# get_settings()는 테스트에서 캐시를 무시하고 재구성해야 할 때 사용한다.
settings = get_settings()
