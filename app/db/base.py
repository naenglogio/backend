from sqlalchemy.orm import DeclarativeBase

from app.db.naming import metadata


class Base(DeclarativeBase):
    """모든 도메인 ORM 모델의 공통 베이스. 실제 모델은 app/domains/{domain}/model.py에 둔다."""

    metadata = metadata
