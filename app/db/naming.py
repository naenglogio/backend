from sqlalchemy import MetaData

# Alembic autogenerate가 제약조건 이름을 안정적으로 비교/생성할 수 있도록
# 테이블/인덱스/외래키/체크 제약의 이름 규칙을 고정한다.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
