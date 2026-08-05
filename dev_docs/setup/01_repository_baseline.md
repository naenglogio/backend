# 1단계 — 저장소 기준선과 구현 경계 확정

## 목표

코드를 바꾸기 전에 현재 저장소를 점검하고 이후 단계가 의존할 기준선을 문서화한다.

## 작업 범위

1. 다음 파일을 확인한다.
   - `pyproject.toml`
   - `Dockerfile`
   - `docker-compose.yml`
   - `.env.example`
   - `alembic.ini`
   - `alembic/env.py`
   - `app/main.py`
   - `app/core/config.py`
   - `dev_docs/backend_direction.md`
   - `dev_docs/{jaeseong,seonyoung,woohee}/`
2. 전체 파일 트리와 현재 실행 경로를 기록한다.
3. 설정 변수, 서비스 이름, 포트, DB 드라이버, Python 버전을 표로 정리한다.
4. 미구현 항목과 팀원 기능 개발의 공통 의존성을 구분한다.
5. 저장소 루트에 중복 문서를 만들지 말고 조사 결과는 이 문서의 `실행 결과` 절 또는 별도의 `dev_docs/setup/current_baseline.md`에 기록한다.

## 반드시 확인할 기준

- API 컨테이너 내부 작업 경로
- 소스 bind mount 경로
- PostgreSQL volume과 healthcheck
- `.env.example`과 코드가 요구하는 변수의 일치 여부
- `/health`의 실제 응답
- Alembic이 DB URL을 어떤 방식으로 변환하는지
- `target_metadata` 상태
- 테스트 및 CI 파일 존재 여부

## 이 단계에서 하지 않을 일

- 패키지 추가
- ORM 모델 생성
- migration 실행
- API 기능 구현
- Docker 서비스 변경

## 검증 명령

```bash
docker compose config
docker compose up -d --build
docker compose ps
docker compose exec api python --version
docker compose exec api python -c "import fastapi, sqlalchemy; print(fastapi.__version__, sqlalchemy.__version__)"
curl http://localhost:8000/health
docker compose down
```

Windows에서 `curl` 별칭 문제가 있으면 브라우저 또는 `Invoke-RestMethod http://localhost:8000/health`를 사용한다.

## 완료 조건

- 현재 구성만으로 컨테이너가 기동되는지 판정했다.
- 구현 전 해결해야 할 blocker가 목록화됐다.
- 다음 단계가 수정해도 되는 파일과 보존해야 하는 파일을 구분했다.

## AI 지시문

```text
이 단계는 조사 단계다. 저장소를 변경하지 말고 현재 구조, 실행 방식, 설정값,
누락된 공통 기반을 분석해 current_baseline.md 초안을 작성해.
명시된 검증 명령을 실행하되 실제 데이터나 볼륨을 삭제하지 마.
```
