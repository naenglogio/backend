# 3단계 — 애플리케이션 공통 코어 구성

## 목표

환경별 설정, 애플리케이션 생명주기, 로깅, 공통 예외 처리, 상태 확인 API를 마련한다.

## 대상 구조

```text
app/
├─ main.py
├─ api/
│  └─ router.py
├─ core/
│  ├─ config.py
│  ├─ logging.py
│  └─ exceptions.py
└─ domains/
```

기존 `app/core/config.py`를 보존하고 확장한다. 공통 HTTP schema가 필요하면 `app/api` 아래에 두며, 도메인 schema는 이후 `app/domains/{domain}/schema.py`에 둔다. 최상위 `app/schemas`는 만들지 않는다.

## 설정 항목

- `APP_NAME`
- `APP_ENV`: `local`, `test`, `development`, `production`
- `DEBUG`
- `API_PREFIX`: 기본 `/api/v1`
- `DATABASE_URL`
- `LOG_LEVEL`
- `CORS_ORIGINS`: 문자열을 안전하게 목록으로 변환

`.env.example`에는 예시만 넣고 비밀번호 실값은 넣지 않는다.

## 구현 작업

1. Pydantic Settings를 캐시된 단일 설정 객체로 제공한다.
2. `create_app()` 팩터리 또는 동일 효과의 명확한 앱 초기화 구조를 만든다.
3. JSON 또는 일관된 구조의 애플리케이션 로그를 설정한다.
4. 예상 가능한 도메인 오류와 예상하지 못한 오류를 공통 응답으로 변환한다.
5. `/health`는 프로세스 생존 확인으로 유지한다.
6. `/ready`는 DB 연결 준비 여부를 확인하게 하되 DB 단계 완료 후 활성화할 수 있게 구성한다.
7. 로컬 프런트엔드 origin만 허용하고 production wildcard를 기본값으로 두지 않는다.
8. `core`에는 비즈니스 규칙이나 특정 도메인 model을 넣지 않는다.

## 공통 오류 응답 예시

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "요청한 리소스를 찾을 수 없습니다.",
  "details": null
}
```

## 완료 조건

- 앱을 import해도 즉시 외부 I/O가 발생하지 않는다.
- 잘못된 환경변수는 시작 시 명확하게 실패한다.
- `/health`가 기존 호환성을 유지한다.
- 예외 응답이 HTML traceback을 사용자에게 노출하지 않는다.

## 검증

```bash
docker compose up -d --build
curl http://localhost:8000/health
curl http://localhost:8000/ready
docker compose logs api
```

## AI 지시문

```text
FastAPI 공통 코어만 구현해. 기존 app/core를 확장하고 인증이나 팀원 기능 Router는 만들지 마.
최상위 app/schemas, app/services, app/repositories를 만들지 마.
기존 /health 호환성을 유지하고 설정·로깅·예외·CORS·앱 초기화 구조를 추가해.
환경변수 기본값과 production 안전성을 구분하고 테스트 가능한 구조로 작성해.
```
