"""merge ingredients and password_resets heads

92a7ff678da3에서 두 갈래로 나뉜 히스토리를 다시 하나로 합친다.

- a1b2c3d4e5f6: ingredients 정본화 (BE-1)
- 105c4a528885: password_resets 테이블 추가

서로 다른 테이블을 건드려 스키마 충돌은 없었지만 head가 2개라
`alembic upgrade head`가 "Multiple head revisions"로 실패했다. 이미 origin에
올라간 리비전의 down_revision을 고치는 대신(팀원 DB의 적용 이력이 깨진다)
alembic 표준 방식인 merge revision으로 정리한다. 스키마 변경은 없다.

Revision ID: 63ff83cd4639
Revises: 105c4a528885, a1b2c3d4e5f6
Create Date: 2026-09-17 14:15:49.752269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63ff83cd4639'
down_revision: Union[str, Sequence[str], None] = ('105c4a528885', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
