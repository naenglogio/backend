# 4단계 — 비동기 DB 기반과 Alembic 연결

## 목표

SQLAlchemy 2 비동기 세션과 ORM 공통 Base를 만들고 Alembic이 모델 metadata를 인식하게 한다.

## 대상 구조

```text
app/db/
├─ base.py
├─ session.py
└─ naming.py
app/domains/
└─ __init__.py
alembic/env.py
```

## 설계 기준

- API 런타임: `postgresql+asyncpg`
- Alembic migration: 현재 방식대로 sync `postgresql+psycopg`
- 요청마다 `AsyncSession`을 열고 요청 종료 시 닫는다.
- service/repository가 commit 경계를 명시하며 dependency가 무조건 commit하지 않는다.
- 테이블/인덱스/외래키 이름은 naming convention으로 안정화한다.
- 시간 저장 기준은 프로젝트 전체에서 하나로 통일한다. 권장은 DB UTC 저장, API에서 timezone 처리다.

## 구현 작업

1. SQLAlchemy `DeclarativeBase`를 정의한다.
2. PK와 timestamp 공통 mixin은 중복을 실제로 줄일 때만 사용한다.
3. async engine과 session factory를 생성한다.
4. FastAPI용 `get_db_session()` dependency를 제공한다.
5. connection pool 설정은 환경변수로 조절 가능하게 하되 로컬 기본값은 단순하게 둔다.
6. Alembic `target_metadata`를 Base metadata에 연결한다.
7. `app.domains` 아래 각 도메인의 model을 명시적으로 import하는 model registry를 구성해 등록 누락을 방지한다.
8. `/ready`에서 `SELECT 1`로 DB 연결을 확인한다.

## 금지사항

- 앱 시작 시 `metadata.create_all()` 사용
- 요청 전역 session 공유
- 비동기 endpoint에서 sync DB 호출
- migration 없이 스키마 자동 변경
- 최상위 `app/models` 생성
- Alembic model 탐색을 위해 무분별한 wildcard import 사용

## 검증

```bash
docker compose up -d --build
docker compose exec api python -c "from app.db.session import engine; print(engine.url.drivername)"
docker compose exec api alembic current
curl http://localhost:8000/ready
```

## 완료 조건

- app DB 연결과 Alembic 연결이 모두 성공한다.
- `target_metadata`가 더 이상 `None`이 아니다.
- DB가 내려가면 `/ready`가 성공으로 오인되지 않는다.

## AI 지시문

```text
SQLAlchemy 2 async 기반의 Base, engine, session dependency를 app/db에 구현하고 Alembic metadata를 연결해.
ORM model은 app/domains/{domain}/model.py에 위치한다는 전제로 registry를 구성하고 app/models는 만들지 마.
런타임 asyncpg와 migration psycopg의 역할을 혼합하지 마.
create_all은 사용하지 말고, 연결 검증과 세션 종료를 테스트해.
```
