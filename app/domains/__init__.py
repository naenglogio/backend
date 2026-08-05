"""도메인 ORM 모델 registry.

Alembic autogenerate는 `app.db.base.Base.metadata`에 등록된 테이블만 인식한다.
각 도메인의 model.py를 여기서 명시적으로 import해 등록 누락을 방지한다.
wildcard import는 사용하지 않는다.
"""

from app.domains.categories import model as categories_model  # noqa: F401
from app.domains.devices import model as devices_model  # noqa: F401
from app.domains.foods import model as foods_model  # noqa: F401
from app.domains.freshness import model as freshness_model  # noqa: F401
from app.domains.ingredients import model as ingredients_model  # noqa: F401
from app.domains.notifications import model as notifications_model  # noqa: F401
from app.domains.products import model as products_model  # noqa: F401
from app.domains.users import model as users_model  # noqa: F401
