"""BE-1: ingredients 테이블을 노션 ERD / API 계약서 정본에 맞춤.

변경 요약
- storage_type: 문자열 enum(REFRIGERATED/FROZEN/ROOM_TEMPERATURE) → int(0/1)
- deletion_reason: WRONG_ENTRY → INCORRECT_ENTRY
- 컬럼 추가: name, quantity, unit, purchase_date, image_url, memo
- expiration_date: NOT NULL → nullable

Revision ID: a1b2c3d4e5f6
Revises: 92a7ff678da3
Create Date: 2026-08-15 23:55:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "92a7ff678da3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) storage_type: CHECK 제거 → 값 변환 → 컬럼 타입을 smallint로 → 0/1 CHECK 추가
    # naming.py에 naming_convention이 등록돼 있어, 이미 확정된 이름을 하드코딩할 때는
    # op.f()로 감싸야 Alembic이 convention을 다시 적용해 이름을 이중으로 만들지 않는다.
    op.drop_constraint(op.f("ck_ingredients_storage_type"), "ingredients", type_="check")
    op.execute(
        """
        UPDATE ingredients
        SET storage_type = CASE storage_type
            WHEN 'REFRIGERATED' THEN '0'
            WHEN 'FROZEN' THEN '1'
            ELSE '0'
        END
        """
    )
    op.alter_column(
        "ingredients",
        "storage_type",
        existing_type=sa.VARCHAR(length=16),
        type_=sa.SmallInteger(),
        existing_nullable=False,
        postgresql_using="storage_type::smallint",
    )
    op.create_check_constraint(
        op.f("ck_ingredients_storage_type_is_refrigerated_or_frozen"),
        "ingredients",
        "storage_type IN (0, 1)",
    )

    # 2) deletion_reason 허용값 교체 (WRONG_ENTRY → INCORRECT_ENTRY)
    op.drop_constraint(op.f("ck_ingredients_deletion_reason"), "ingredients", type_="check")
    # 기존 컬럼은 'WRONG_ENTRY'(11자) 기준 VARCHAR(11). 'INCORRECT_ENTRY'(15자)를
    # 담으려면 먼저 폭을 넓혀야 UPDATE가 안 잘린다.
    op.alter_column(
        "ingredients",
        "deletion_reason",
        existing_type=sa.VARCHAR(length=11),
        type_=sa.VARCHAR(length=16),
        existing_nullable=True,
    )
    op.execute(
        """
        UPDATE ingredients
        SET deletion_reason = 'INCORRECT_ENTRY'
        WHERE deletion_reason = 'WRONG_ENTRY'
        """
    )
    op.create_check_constraint(
        op.f("ck_ingredients_deletion_reason"),
        "ingredients",
        "deletion_reason IN ('CONSUMED', 'DISCARDED', 'INCORRECT_ENTRY')",
    )

    # 3) 누락 필드 추가. name은 NOT NULL이라 기존 행을 foods.name으로 먼저 채운 뒤 NOT NULL 적용
    op.add_column(
        "ingredients",
        sa.Column("name", sa.String(length=255), nullable=True),
    )
    op.execute(
        """
        UPDATE ingredients AS i
        SET name = f.name
        FROM foods AS f
        WHERE i.food_id = f.id AND i.name IS NULL
        """
    )
    op.alter_column("ingredients", "name", nullable=False)

    # quantity는 기존 행 때문에 잠시 server_default=1을 쓰고, 마지막에 제거한다.
    op.add_column(
        "ingredients",
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column("ingredients", sa.Column("unit", sa.String(length=30), nullable=True))
    op.add_column("ingredients", sa.Column("purchase_date", sa.Date(), nullable=True))
    op.add_column("ingredients", sa.Column("image_url", sa.Text(), nullable=True))
    op.add_column("ingredients", sa.Column("memo", sa.Text(), nullable=True))

    # 4) 계약서: expiration_date는 모를 수 있으므로 nullable
    op.alter_column(
        "ingredients",
        "expiration_date",
        existing_type=sa.Date(),
        nullable=True,
    )

    # 모델의 Python default와 겹치지 않도록 DB server_default는 제거
    op.alter_column("ingredients", "quantity", server_default=None)


def downgrade() -> None:
    # upgrade의 역순. BE-1 이전 스키마로 되돌린다.
    op.alter_column(
        "ingredients",
        "expiration_date",
        existing_type=sa.Date(),
        nullable=False,
    )

    op.drop_column("ingredients", "memo")
    op.drop_column("ingredients", "image_url")
    op.drop_column("ingredients", "purchase_date")
    op.drop_column("ingredients", "unit")
    op.drop_column("ingredients", "quantity")
    op.drop_column("ingredients", "name")

    op.drop_constraint(op.f("ck_ingredients_deletion_reason"), "ingredients", type_="check")
    op.execute(
        """
        UPDATE ingredients
        SET deletion_reason = 'WRONG_ENTRY'
        WHERE deletion_reason = 'INCORRECT_ENTRY'
        """
    )
    # upgrade에서 넓힌 폭을 원복. 이 시점엔 값이 전부 11자 이하로 되돌아가 있다.
    op.alter_column(
        "ingredients",
        "deletion_reason",
        existing_type=sa.VARCHAR(length=16),
        type_=sa.VARCHAR(length=11),
        existing_nullable=True,
    )
    op.create_check_constraint(
        op.f("ck_ingredients_deletion_reason"),
        "ingredients",
        "deletion_reason IN ('CONSUMED', 'DISCARDED', 'WRONG_ENTRY')",
    )

    op.drop_constraint(
        op.f("ck_ingredients_storage_type_is_refrigerated_or_frozen"),
        "ingredients",
        type_="check",
    )
    op.alter_column(
        "ingredients",
        "storage_type",
        existing_type=sa.SmallInteger(),
        type_=sa.VARCHAR(length=16),
        existing_nullable=False,
        postgresql_using=(
            "CASE storage_type "
            "WHEN 0 THEN 'REFRIGERATED' "
            "WHEN 1 THEN 'FROZEN' "
            "ELSE 'REFRIGERATED' END"
        ),
    )
    op.create_check_constraint(
        op.f("ck_ingredients_storage_type"),
        "ingredients",
        "storage_type IN ('REFRIGERATED', 'FROZEN', 'ROOM_TEMPERATURE')",
    )
