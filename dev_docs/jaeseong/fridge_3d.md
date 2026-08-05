메인 3D 냉장고 Backend 지시서

목표

3D 화면이 사용자의 현재 냉장·냉동 식재료를 렌더링할 수 있도록 최소 데이터를 제공한다.

데이터 기준

ingredients.user_id = current_user.id
ingredients.is_deleted = false

storage_type에 따라 냉장·냉동 영역을 구분한다.

응답 필드 후보

ingredient_id
food_id
name
storage_type
quantity
unit
expiration_date
expiration_status
image_url

AI 구현 지시문

3D 냉장고 메인 화면용 조회 기능을 구현하라.

필수 조건:

- 기존 ingredients 목록 service를 재사용한다.
- 미삭제 식재료만 반환한다.
- storage_type 기준으로 냉장과 냉동을 그룹화한다.
- 3D 좌표와 사용자별 레이아웃을 DB에 저장하지 않는다.
- API 전용 중복 query를 만들기 전에 기존 목록 API로 충족 가능한지 검토한다.
- N+1 query와 불필요한 전체 컬럼 조회를 점검한다.

새 endpoint가 필요하지 않다면 기존 목록 API의 response 확장안을 먼저 제시하라.
