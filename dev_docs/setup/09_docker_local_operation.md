# 9단계 — Docker 로컬 실행 표준화

## 목표

팀원 PC의 로컬 경로와 Python 설치 상태가 달라도 동일한 명령으로 백엔드를 실행하게 한다.

## 핵심 원칙

- GitHub에서 clone한 로컬 절대경로는 팀원마다 달라도 된다.
- 모든 명령은 저장소 루트에서 실행한다.
- 컨테이너 내부 경로, Compose service 이름, volume 이름은 팀 공통이다.
- `.env.example`은 공유하고 `.env`는 각자 생성한다.

## 점검 대상

- Dockerfile의 non-root 실행 가능 여부
- API healthcheck 유무
- Compose의 DB healthcheck와 `depends_on`
- Windows bind mount에서 reload 동작
- migration 실행 주체
- test DB 분리
- named volume 보존 정책
- API 컨테이너에서 batch command를 같은 설정과 DB 연결로 실행할 수 있는지

## 표준 최초 실행

```bash
git clone https://github.com/naenglogio/backend.git
cd backend
copy .env.example .env
docker compose config
docker compose up -d --build
docker compose run --rm api alembic upgrade head
docker compose run --rm api python -m app.db.seed
docker compose ps
```

PowerShell에서는 `Copy-Item .env.example .env`, macOS/Linux에서는 `cp .env.example .env`를 사용한다.

## 표준 개발 명령

```bash
docker compose up -d
docker compose logs -f api
docker compose exec api pytest -q
docker compose exec api ruff check .
docker compose run --rm api python -m app.batch.runner --help
docker compose down
```

## 데이터 초기화 주의

`docker compose down -v`는 PostgreSQL volume을 삭제한다. 일반 종료 명령으로 문서화하지 않으며, 사용자가 로컬 데이터 전체 삭제를 명확히 의도할 때만 실행한다.

## 완료 조건

- 새 clone에서 수동 Python 가상환경 없이 API·DB·migration·seed가 실행된다.
- Windows와 macOS/Linux 명령 차이가 문서화됐다.
- 데이터 보존/삭제 명령이 명확히 구분됐다.
- 별도 크롤러를 Compose에 억지로 합치지 않고 백엔드 batch entrypoint만 실행 가능하다.

## AI 지시문

```text
현재 Docker 구성을 기반으로 팀 공통 로컬 실행 절차를 완성해.
로컬 절대경로를 문서나 Compose에 하드코딩하지 마.
기존 DB volume을 자동 삭제하지 말고, healthcheck·migration·seed·테스트 실행을 검증해.
```
