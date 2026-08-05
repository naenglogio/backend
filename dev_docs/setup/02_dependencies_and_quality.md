# 2단계 — 의존성 및 코드 품질 도구 설정

## 목표

모든 팀원이 동일한 Python 의존성과 검사 규칙을 사용하게 한다.

## 권장 결정

- 운영 의존성과 개발 의존성을 `pyproject.toml`에서 구분한다.
- 패키지 잠금 도구는 하나만 선택한다. 프로젝트가 새롭다면 `uv.lock`을 사용하는 방식을 우선 검토한다.
- Formatter/Linter는 Ruff, 타입 검사는 mypy, 테스트는 pytest를 권장한다.
- 한 번 선택한 도구는 Docker와 CI에서 동일하게 실행한다.

## 필요한 개발 의존성

- `pytest`
- `pytest-asyncio`
- `httpx`
- `ruff`
- `mypy`

필요성이 확인되기 전에는 인증, OCR, AI, 지도 SDK를 공통 단계에서 추가하지 않는다.

## 구현 작업

1. `pyproject.toml`에 개발 의존성 그룹을 추가한다.
2. Ruff 설정에 Python 3.12와 프로젝트 소스 경로를 반영한다.
3. mypy는 처음부터 지나치게 엄격하게 두지 말고 앱 코드에서 점진 적용 가능하게 한다.
4. pytest의 test path와 asyncio mode를 명시한다.
5. 선택한 잠금 파일을 생성하고 커밋 대상에 포함한다.
6. `.gitignore`에 Python cache, test cache, coverage, IDE, `.env` 규칙을 점검한다.

## 권장 명령 인터페이스

```bash
ruff check .
ruff format --check .
mypy app
pytest
```

## 주의사항

- 기존 운영 dependency 버전을 무조건 대규모 업그레이드하지 않는다.
- `requirements.txt`, Poetry, uv를 동시에 운영하지 않는다.
- 자동 format으로 팀원 문서를 대량 변경하지 않는다.

## 완료 조건

- 새 환경에서 잠금 파일만으로 재현 가능하다.
- 네 가지 품질 명령이 실행된다.
- 아직 없는 앱 계층 때문에 실패하는 규칙은 이유를 기록하고 최소한으로 예외 처리한다.

## AI 지시문

```text
현재 pyproject.toml의 운영 의존성은 보존해.
개발 의존성 그룹과 Ruff, mypy, pytest 설정을 추가하고 하나의 잠금 전략만 적용해.
검사 제외는 파일 전체가 아니라 필요한 최소 범위로 설정하고, 각 검증 명령의 결과를 보고해.
```
