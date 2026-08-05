# 10단계 — CI와 협업 기준

## 목표

팀원별 기능 branch가 공통 기반을 깨뜨리지 않도록 GitHub Actions와 PR 기준을 마련한다.

## CI 필수 작업

1. dependency 설치와 cache
2. `ruff check .`
3. `ruff format --check .`
4. `mypy app`
5. PostgreSQL service 기동
6. `alembic upgrade head`
7. `pytest -q`

## Git 전략 권장안

- 기본 branch: `main`
- 공통 세팅 branch: `chore/backend-foundation`
- 팀원 기능 branch: `feat/{owner}/{feature}`
- 공통 세팅을 먼저 merge한 뒤 각 기능 branch는 최신 `main`을 기준으로 시작한다.
- migration 파일명은 목적을 드러내고 동시에 여러 migration PR이 생기면 revision 충돌을 확인한다.
- 팀원 기능은 담당 `app/domains/{domain}`을 중심으로 변경하고 공통 `core`, `db`, `api`, `batch` 변경은 영향 범위를 공유한다.

## PR 체크리스트

- [ ] 범위 밖 변경이 없다.
- [ ] 새 환경변수를 `.env.example`에 반영했다.
- [ ] schema 변경에 migration이 있다.
- [ ] downgrade 또는 롤백 가능성을 확인했다.
- [ ] API 계약 변경을 문서화했다.
- [ ] Mock과 실제 adapter 경계를 유지했다.
- [ ] 테스트와 정적 검사가 통과한다.
- [ ] 비밀값, 개인 경로, 생성 데이터가 포함되지 않았다.

## 역할 경계

- 재성: 공통 기반, 카메라 인식 연계, 식재료 등록/상세, 3D 메인 연계
- 선영: 알림, 지도/마트, 추천, 식재료 목록
- 우희: 로그인/회원가입/내정보, AI 챗봇
- SNS 로그인은 현재 범위에서 제외한다.

공통 파일 변경이 필요한 기능은 소유자가 독단 변경하지 않고 영향받는 팀원과 API/DB 계약을 확인한다.

도메인 소유권은 파일 독점권이 아니라 변경 조율 기준이다. 여러 기능이 사용하는 `ingredients`, `users`, `notifications` 계약은 PR에서 영향받는 담당자 검토를 받는다.

## 완료 조건

- PR에서 코드 검사, migration, 테스트가 자동 수행된다.
- CI가 실제 앱과 같은 Python/DB 주요 버전을 사용한다.
- 팀원 기능 개발 branch가 공통 세팅 완료 커밋을 기준으로 만들어진다.

## AI 지시문

```text
GitHub Actions에 lint, format check, type check, PostgreSQL migration, test job을 구성해.
실제 secret 없이 테스트 전용 환경변수를 사용하고, 로그에 비밀값을 출력하지 마.
CI 전용 편법 대신 로컬과 동일한 명령을 재사용해.
```
