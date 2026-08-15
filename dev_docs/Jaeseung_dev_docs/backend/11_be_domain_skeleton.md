# BE-2. ingredients 도메인 파일 세트

## 선행
BE-1 완료 (모델 확정).

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md`
- 기존 `app/domains/users/`의 schema.py/service.py/router.py (패턴 참고)
- `app/api/router.py`, `app/api/schemas.py`(Page, COMMON_ERROR_RESPONSES)

## 지시
`users` 도메인과 동일한 패턴으로 ingredients 도메인의 `schema.py` / `repository.py` / `service.py` / `router.py`를 만들어라. 이번 테스크는 **뼈대와 계약**까지 (실제 엔드포인트 로직은 BE-3~5에서 채운다).

- `schema.py`: 계약서의 요청/응답 스키마 정의. 필드·enum은 노션 정본 + 프론트 `types/features`와 1:1.
- `repository.py`: DB 질의 담당 (여기에만 ORM).
- `service.py`: 업무 규칙 + 트랜잭션 경계.
- `router.py`: HTTP 입출력·상태코드만. ORM 금지.
- `app/api/router.py`에 `include_router(ingredients_router, prefix="/ingredients", tags=["ingredients"])` 등록.

## 체크포인트
- [ ] 계층 경계 준수 (router에 ORM 없음)
- [ ] schema가 계약서/프론트 features 타입과 1:1
- [ ] `Page[T]`·`COMMON_ERROR_RESPONSES` 사용
- [ ] router가 `/api/v1/ingredients`로 등록됨 (Swagger에 노출)

## 완료 후
`../shared/01_STATUS_BOARD.md`의 BE-2 → ✅.
