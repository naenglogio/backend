# NaengLog Backend

FastAPI + PostgreSQL(pgvector) + SQLAlchemy 2.0 + Alembic

## 로컬 개발 환경 세팅

1. `.env.example`을 복사해서 `.env` 생성
2. Docker 이미지 빌드 및 실행
3. 마이그레이션 적용
4. http://localhost:8000/health 접속해서 확인

## Docker 명령어

### 빌드 및 실행

```bash
docker compose build
docker compose up -d
docker compose exec api alembic upgrade head
```

한 번에 빌드하고 실행하려면:

```bash
docker compose up -d --build
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
