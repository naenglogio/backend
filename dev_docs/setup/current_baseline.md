# 저장소 기준선 (1단계 조사 결과)

- 조사 시각: 2026-08-05
- 조사 기준 커밋(HEAD): `864ef8fb35b441c81cd9b10ac4a14b26ce474658` ("feat: Harness_md setup")
- `00_setup_direction.md`에 명시된 확인 기준 커밋(`0d494b671d3fd8cf4a91d9c40ca7bd129165c1a9`) 이후 커밋 1개(`864ef8f`)가 추가로 존재함. `dev_docs/setup/*.md` 다수 파일도 HEAD 대비 워킹트리에서 미커밋 수정 상태(`git status` 상 `M`)이며, `02_dependencies_and_quality.md`만 HEAD와 동일함.

## 1. 전체 파일 트리 (추적 대상, venv/__pycache__ 제외)

```text
.env.example
.gitignore
Dockerfile
README.md
alembic.ini
alembic/README
alembic/env.py
alembic/script.py.mako
app/__init__.py
app/batch/.gitkeep
app/core/__init__.py
app/core/config.py
app/core/database.py
app/domains/__init__.py
app/main.py
app/shared/__init__.py
app/shared/base_model.py
docker-compose.yml
pyproject.toml
tests/__init__.py
dev_docs/mock_data_policy.md
dev_docs/jaeseong/*.md (4개 문서 존재)
dev_docs/seungyeong/  (빈 디렉터리, 문서 없음)
dev_docs/woohee/      (빈 디렉터리, 문서 없음)
dev_docs/setup/*.md   (12개, 이 문서 포함)
```

로컬 전용(미추적, `.gitignore` 처리): `.env`, `venv/`, `__pycache__/`

## 2. 설정값 / 실행 경로 표

| 항목 | 값 |
|---|---|
| API 컨테이너 작업 경로 | `/app` (Dockerfile `WORKDIR /app`) |
| 소스 bind mount | `.:/app` (docker-compose.yml, api 서비스) |
| API 포트 | 호스트 `8000` → 컨테이너 `8000` |
| DB 이미지 | `pgvector/pgvector:pg16` |
| DB volume | `pgdata:/var/lib/postgresql/data` (named volume) |
| DB healthcheck | `pg_isready -U ${POSTGRES_USER}` (5s interval, 5 retries) |
| Python 버전 (pyproject) | `>=3.12` |
| Python 버전 (Dockerfile) | `python:3.12-slim` |
| Python 버전 (로컬 호스트) | `3.11.5` — 컨테이너 기준과 다름. Docker로만 실행하면 문제 없음 |
| 런타임 DB 드라이버 | `asyncpg` (`app/core/database.py`) |
| Migration DB 드라이버 | `psycopg` — `alembic/env.py`가 `postgresql+asyncpg` → `postgresql+psycopg` 문자열 치환으로 변환 |
| 설정 로더 | `app/core/config.py`의 `Settings(BaseSettings)`, `.env` 파일 기반 |
| API 프리픽스 | 없음 (`/health`만 최상위에 직접 등록) |

## 3. `.env.example` vs 코드 요구 변수

- `.env.example`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`
- `app/core/config.py`가 요구하는 변수: `DATABASE_URL` 단 하나 (`extra="ignore"`라 나머지는 무시됨)
- 3단계(`03_application_core.md`)에서 요구하는 `APP_NAME`, `APP_ENV`, `DEBUG`, `API_PREFIX`, `LOG_LEVEL`, `CORS_ORIGINS`는 아직 `.env.example`과 `Settings` 어디에도 없음 → 3단계에서 추가 필요.

## 4. `/health` 실제 응답

`app/main.py` 기준:

```python
@app.get("/health")
def health_check():
    return {"status": "ok"}
```

동기 함수, 인증 없음, DB 접근 없음. 단순 프로세스 생존 확인용. `/ready`는 아직 없음.

## 5. Alembic 상태

- `alembic.ini`의 `sqlalchemy.url`은 placeholder(`driver://user:pass@localhost/dbname`)이며 실제로는 `alembic/env.py`가 `settings.DATABASE_URL`을 읽어 런타임에 덮어씀.
- `target_metadata = None` → 현재 `--autogenerate`로 모델 기반 migration 생성 불가 (4~5단계에서 해결 대상, 00번 문서에 이미 명시된 known issue).
- `alembic/versions/` 디렉터리 자체가 아직 없음 (최초 migration 없음).

## 6. 테스트 / CI 존재 여부

- `tests/__init__.py`만 존재, 실제 테스트 파일 없음.
- `pyproject.toml`에 `[tool.pytest.ini_options]`, `[tool.ruff]`, `[tool.mypy]` 등 품질 도구 설정 없음. dev dependency 그룹도 없음.
- `.github/` 디렉터리 없음 → CI 워크플로 없음 (10단계 대상, 예정대로).
- 잠금 파일(`uv.lock` 등) 없음.

## 7. `app/core`, `app/domains`, `app/batch` 현황 (보존 대상)

| 경로 | 내용물 | 상태 |
|---|---|---|
| `app/core/__init__.py` | 빈 파일 | 보존 |
| `app/core/config.py` | `Settings` (DATABASE_URL만) | 보존 후 3단계에서 확장 |
| `app/core/database.py` | `create_async_engine`, `async_sessionmaker` | 보존, 4단계에서 `app/db`로 이전 여부 결정 필요 (§9 참고) |
| `app/domains/__init__.py` | 빈 파일 | 보존, 하위 도메인 패키지(users/devices/...)는 아직 미생성 |
| `app/batch/.gitkeep` | placeholder | 보존, 실제 batch 로직 없음 |

## 8. 최상위 계층형 구조와 도메인 구조 혼합 여부

- `app/shared/` 디렉터리가 존재하며 `base_model.py`(SQLAlchemy `DeclarativeBase`)를 담고 있음.
- `00_setup_direction.md`의 목표 디렉터리 구조에는 `app/shared`가 없고, "DB 연결, ORM Base, 세션 같은 기술 공통 요소만 `app/db`에 둔다"고 명시되어 있음.
- 즉 현재 ORM `Base`(`app/shared/base_model.py`)와 세션/엔진(`app/core/database.py`)이 목표 구조상의 `app/db` 위치가 아닌 두 곳(`app/shared`, `app/core`)에 분산되어 있음 → **최상위 계층형 잔재로 판단됨.**
- 이는 1~3단계 범위(조사/의존성/앱 코어) 밖의 사안이며, 4단계(`04_database_foundation.md`, "Async DB 세션·Base·Alembic 연결")에서 `app/db`로 통합 이전할지 결정해야 함. 지금은 코드를 변경하지 않고 기록만 남김.

## 9. 미구현 항목 vs 팀원 기능 개발 공통 의존성 구분

**공통 기반 미구현 (이 setup 트랙에서 채워야 할 것, 1~11단계 대상):**
- 개발 의존성/린트·타입체크·테스트 설정 (2단계)
- 환경설정 확장, 로깅, 예외 처리, `/ready` (3단계)
- DB Base/세션 정리 위치, Alembic 연결 완성 (4단계)
- MVP 8개 테이블 모델 및 최초 migration (5단계)
- 공통 Router 조립, 응답/오류 규격 (6단계)
- Mock/Seed 데이터 (7단계)
- 테스트 기반 (8단계)
- Docker 로컬 운영 절차 문서화 (9단계)
- CI (10단계)

**팀원 기능 개발 몫 (이 setup 트랙 범위 밖):**
- `app/domains/{users,devices,categories,foods,products,freshness,ingredients,notifications}` 내부의 실제 model/schema/repository/service/router 구현
- 인증 방식, 카메라 인식, 3D 냉장고, 크롤링·OCR 파이프라인 등 `dev_docs/jaeseong/*` 및 팀원별 문서에 기술된 기능 요구사항

## 10. 발견된 이슈 / 확인 필요 사항 (blocker 여부 판단)

1. **`dev_docs/backend_direction.md` 없음** — `00_setup_direction.md`와 `01_repository_baseline.md`가 공통 상위 기준 문서로 지정하고 있으나 저장소에 존재하지 않음. 1~3단계(조사/의존성/앱 코어)는 이 문서 없이도 진행 가능하나, 5단계(MVP 모델/ERD)부터는 이 문서 또는 대체 기준이 필요함. **지금 당장 blocker는 아님.**
2. **`dev_docs/{seungyeong,woohee}/` 비어 있음** — 두 팀원 문서가 아직 작성되지 않음. 공통 기반 구축(1~11단계)에는 영향 없음.
3. **`app/shared` vs 목표 구조의 `app/db` 불일치** (§8) — 4단계 진행 시 재확인 및 결정 필요. **1~3단계 진행에는 영향 없음.**
4. **로컬 호스트 Python(3.11.5)이 pyproject 요구사항(≥3.12)보다 낮음** — Docker 컨테이너는 3.12라 실행에는 문제 없으나, 로컬(비Docker) 환경에서 `ruff`/`mypy`/`pytest`를 직접 돌리는 팀원은 별도 3.12 가상환경이 필요함. 2단계 보고 시 안내 필요.
5. **`docker-compose.yml`의 obsolete `version: "3.9"` 키** — Compose v2에서 무시되고 경고만 발생. 기능 영향 없음, 정리는 선택사항.

## 11. 1단계 검증 명령 실행 결과

| 명령 | 결과 |
|---|---|
| `docker compose config` | 통과. `version` 속성 obsolete 경고만 있음 |
| `docker compose up -d --build` | 통과. `db`(healthy) → `api` 순서로 정상 기동 |
| `docker compose ps` | 통과. `api`: `Up`, `db`: `Up (healthy)` |
| `exec api python --version` | `Python 3.12.13` |
| `exec api python -c "import fastapi, sqlalchemy; print(...)"` | `fastapi 0.139.0`, `sqlalchemy 2.0.51` |
| `curl http://localhost:8000/health` | `{"status":"ok"}` |
| `docker compose down` | 통과. 컨테이너/네트워크 정리, `pgdata` volume은 보존(삭제 안 함) |

## 12. 다음 단계가 수정해도 되는 파일 vs 보존해야 하는 파일

**보존 (삭제/구조 대체 금지, 00번 문서 원칙):**
- `app/core/`, `app/domains/`, `app/batch/` 자체 (내부 확장은 허용)
- `dev_docs/jaeseong/*`, `dev_docs/mock_data_policy.md`

**수정 가능 (해당 단계 범위 내):**
- `pyproject.toml` (2단계: dev deps/tool 설정 추가, 기존 운영 의존성 보존)
- `.gitignore` (2단계: 캐시/커버리지 규칙 보강)
- `app/core/config.py`, `app/main.py`, 신규 `app/api/router.py`, `app/core/logging.py`, `app/core/exceptions.py` (3단계)
- `.env.example` (3단계: 신규 설정 키 예시 추가, 실값 금지)

**결정 보류 (4단계에서 재논의):**
- `app/shared/base_model.py`, `app/core/database.py`의 최종 위치 (`app/db`로 통합 여부)
