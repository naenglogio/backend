# NaengLog Backend

FastAPI + PostgreSQL(pgvector) + SQLAlchemy 2.0 + Alembic

## 로컬 개발 환경 세팅

1. .env.example을 복사해서 .env 생성
2. docker compose up -d
3. docker compose exec api alembic upgrade head
4. http://localhost:8000/health 접속해서 확인
5. (선택) http://localhost:5050 에서 pgAdmin 접속
   - 로그인: `.env`의 `PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD` (기본 `admin@naenglog.io` / `changeme`)
   - Add New Server → Host `db`, Port `5432`, Username/Password/DB는 `POSTGRES_*` 값

## Docker 명령어

### 최초 실행 (또는 Dockerfile / 의존성 변경 후)

이미지를 새로 빌드한 뒤 컨테이너를 띄웁니다.

```bash
docker compose build
docker compose up -d
docker compose exec api alembic upgrade head
```

한 줄로 빌드+실행하려면:

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
```

### 이미 빌드된 이미지가 있을 때

빌드 없이 컨테이너만 다시 실행합니다.

```bash
docker compose up -d
```

마이그레이션이 아직 안 되어 있거나 새로 추가된 경우:

```bash
docker compose exec api alembic upgrade head
```

### 종료

```bash
docker compose down
```

DB 데이터(volume)까지 삭제하려면:

```bash
docker compose down -v
```
