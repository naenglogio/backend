식재료 카메라 인식 Backend 지시서

MVP 목표

촬영 이미지를 인식 모듈 또는 외부 AI API에 전달하고, foods와 products에서 등록 후보를 찾아 반환한다. 인식 결과를 자동 저장하지 않는다.

흐름

촬영 이미지
→ 이미지 형식·크기 검증
→ Recognition Adapter
→ 표준 식재료 후보
→ foods·products 조회
→ 후보 목록 반환
→ 사용자 선택
→ ingredients 등록 API 호출

응답 예시

{
"candidates": [
{
"food_id": 101,
"food_name": "계란",
"product_id": null,
"confidence_score": 0.91
}
]
}

AI 구현 지시문

식재료 카메라 인식의 MVP adapter와 후보 응답 API를 구현하라.

필수 조건:

- 인식 엔진을 interface로 추상화한다.
- Router에서 모델을 직접 호출하지 않는다.
- 파일 형식과 최대 크기를 검증한다.
- timeout과 외부 오류를 도메인 오류로 변환한다.
- 테스트에서는 fake recognition adapter를 사용한다.
- 인식 로그, 이미지 임베딩, 재학습 테이블을 만들지 않는다.
- 결과를 ingredients에 자동 저장하지 않는다.

API, adapter interface, fake adapter, service, schema와 테스트만 구현하라.
실제 AI 모델 선택이나 학습은 이번 작업 범위에서 제외한다.
