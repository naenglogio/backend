# NaengLog Backend

FastAPI + PostgreSQL(pgvector) + SQLAlchemy 2.0 + Alembic

## 로컬 개발 환경 세팅

1. .env.example을 복사해서 .env 생성
2. docker compose up -d
3. docker compose exec api alembic upgrade head
4. http://localhost:8000/health 접속해서 확인
