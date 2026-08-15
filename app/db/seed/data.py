"""로컬 개발용 seed 데이터 정의.

여기 있는 값(email, push_token, 카테고리/식품 이름, 외부 상품 ID)은 idempotent
get-or-create와 reset 범위 제한에 쓰이는 고정 식별자다. 값을 바꾸면 재실행 시
새 행이 또 생기니 함부로 바꾸지 않는다.

seed 비밀번호 해시는 실제 로그인에 쓸 수 없는 placeholder다(인증 기능 자체가
아직 없다). 실제 인증이 만들어지면 이 값을 실제 해시 유틸로 교체한다.
"""

from typing import Any

SEED_PASSWORD_HASH_PLACEHOLDER = "seed-placeholder-hash-not-for-login"

SEED_USERS: list[dict[str, Any]] = [
    {"email": "seed.user1@naenglog.local", "notification_agreed": True},
    {"email": "seed.user2@naenglog.local", "notification_agreed": False},
    {"email": "seed.user3@naenglog.local", "notification_agreed": True},
]
SEED_USER_EMAILS: list[str] = [u["email"] for u in SEED_USERS]

SEED_DEVICES: list[dict[str, Any]] = [
    {"user_email": "seed.user1@naenglog.local", "push_token": "seed-device-token-1"},
    {"user_email": "seed.user2@naenglog.local", "push_token": "seed-device-token-2"},
    {"user_email": "seed.user3@naenglog.local", "push_token": "seed-device-token-3"},
]

SEED_CATEGORY_NAMES: list[str] = ["유제품", "채소", "가공식품"]

SEED_FOODS: list[dict[str, Any]] = [
    {"name": "우유", "category_name": "유제품"},
    {"name": "계란", "category_name": "유제품"},
    {"name": "양파", "category_name": "채소"},
    {"name": "당근", "category_name": "채소"},
    {"name": "즉석밥", "category_name": "가공식품"},
    {"name": "냉동만두", "category_name": "가공식품"},
]

SEED_PRODUCTS: list[dict[str, Any]] = [
    {
        "external_id": "seed-prod-1001",
        "source": "KURLY",
        "name": "컬리 우유 1L",
        "food_name": "우유",
    },
    {
        "external_id": "seed-prod-1002",
        "source": "KURLY",
        "name": "컬리 계란 15구",
        "food_name": "계란",
    },
    {
        "external_id": "seed-prod-2001",
        "source": "N_MART",
        "name": "N마트 양파 1kg",
        "food_name": "양파",
    },
    {
        "external_id": "seed-prod-2002",
        "source": "N_MART",
        "name": "N마트 당근 500g",
        "food_name": "당근",
    },
    {
        "external_id": "seed-prod-1003",
        "source": "KURLY",
        "name": "컬리 즉석밥",
        "food_name": "즉석밥",
    },
    {
        "external_id": "seed-prod-1004",
        "source": "KURLY",
        "name": "컬리 냉동만두",
        "food_name": "냉동만두",
    },
]

# food_name + product_external_id 조합으로 ingredient가 참조한다.
SEED_FRESHNESS_PROFILES: list[dict[str, Any]] = [
    {
        "food_name": "우유",
        "product_external_id": "seed-prod-1001",
        "storage_type": "REFRIGERATED",
        "expiration_days": 10,
        "expiration_source": "PRODUCT_DISCLOSURE",
        "expiration_status": "CONFIRMED",
    },
    {
        "food_name": "냉동만두",
        "product_external_id": "seed-prod-1004",
        "storage_type": "FROZEN",
        "expiration_days": 180,
        "expiration_source": "PRODUCT_DISCLOSURE",
        "expiration_status": "CONFIRMED",
    },
    {
        "food_name": "즉석밥",
        "product_external_id": "seed-prod-1003",
        "storage_type": "ROOM_TEMPERATURE",
        "expiration_days": 365,
        "expiration_source": "PRODUCT_DISCLOSURE",
        "expiration_status": "ESTIMATED",
    },
]

# key는 SEED_NOTIFICATIONS가 어떤 ingredient를 가리키는지 연결하는 용도로만 쓰는
# seed 내부 식별자다. DB 컬럼이 아니다.
#
# BE-1 반영:
# - storage_type: 문자열 → int (0=냉장, 1=냉동)
# - name/quantity/unit 등 새 필드
# - deletion_reason: WRONG_ENTRY → INCORRECT_ENTRY
SEED_INGREDIENTS: list[dict[str, Any]] = [
    # --- 활성 상태: 임박/여유/경과 각 1건 ---
    {
        "key": "user1-milk-soon",
        "user_email": "seed.user1@naenglog.local",
        "food_name": "우유",
        "product_external_id": "seed-prod-1001",
        "use_profile": True,
        "name": "우유",
        "storage_type": 0,  # 냉장
        "quantity": 1,
        "expiration_offset_days": 2,  # 임박
        "expiration_source": "PRODUCT_DISCLOSURE",
        "expiration_status": "CONFIRMED",
        "is_deleted": False,
        "deletion_reason": None,
    },
    {
        "key": "user2-carrot-comfortable",
        "user_email": "seed.user2@naenglog.local",
        "food_name": "당근",
        "product_external_id": "seed-prod-2002",
        "use_profile": False,
        "name": "당근",
        "storage_type": 0,
        "quantity": 2,
        "unit": "개",
        "expiration_offset_days": 30,  # 여유
        "expiration_source": "PRODUCT_DISCLOSURE",
        "expiration_status": "ESTIMATED",
        "is_deleted": False,
        "deletion_reason": None,
    },
    {
        "key": "user3-onion-overdue",
        "user_email": "seed.user3@naenglog.local",
        "food_name": "양파",
        "product_external_id": None,  # 직접 입력 식재료 예시
        "use_profile": False,
        "name": "양파",
        "storage_type": 0,  # 냉장 (ROOM_TEMPERATURE는 정본에서 제거)
        "quantity": 1,
        "expiration_offset_days": -3,  # 경과
        "expiration_source": "USER_INPUT",
        "expiration_status": "CONFIRMED",
        "is_deleted": False,
        "deletion_reason": None,
    },
    # --- soft-deleted: CONSUMED / DISCARDED / INCORRECT_ENTRY 각 1건 ---
    {
        "key": "user1-egg-consumed",
        "user_email": "seed.user1@naenglog.local",
        "food_name": "계란",
        "product_external_id": "seed-prod-1002",
        "use_profile": False,
        "name": "계란",
        "storage_type": 0,
        "quantity": 1,
        "expiration_offset_days": -10,
        "expiration_source": "PRODUCT_DISCLOSURE",
        "expiration_status": "CONFIRMED",
        "is_deleted": True,
        "deletion_reason": "CONSUMED",
    },
    {
        "key": "user2-dumpling-discarded",
        "user_email": "seed.user2@naenglog.local",
        "food_name": "냉동만두",
        "product_external_id": "seed-prod-1004",
        "use_profile": True,
        "name": "냉동만두",
        "storage_type": 1,  # 냉동
        "quantity": 1,
        "expiration_offset_days": 100,
        "expiration_source": "PRODUCT_DISCLOSURE",
        "expiration_status": "CONFIRMED",
        "is_deleted": True,
        "deletion_reason": "DISCARDED",
    },
    {
        "key": "user3-rice-incorrect-entry",
        "user_email": "seed.user3@naenglog.local",
        "food_name": "즉석밥",
        "product_external_id": "seed-prod-1003",
        "use_profile": True,
        "name": "즉석밥",
        "storage_type": 0,
        "quantity": 1,
        "expiration_offset_days": 300,
        "expiration_source": "PRODUCT_DISCLOSURE",
        "expiration_status": "ESTIMATED",
        "is_deleted": True,
        "deletion_reason": "INCORRECT_ENTRY",
    },
]

SEED_NOTIFICATIONS: list[dict[str, Any]] = [
    {
        "user_email": "seed.user1@naenglog.local",
        "ingredient_key": "user1-milk-soon",
        "message": "우유의 소비기한이 얼마 남지 않았어요.",
        "is_read": False,
    },
    {
        "user_email": "seed.user1@naenglog.local",
        "ingredient_key": "user1-egg-consumed",
        "message": "계란을 소비 완료로 기록했어요.",
        "is_read": True,
    },
    {
        "user_email": "seed.user2@naenglog.local",
        "ingredient_key": "user2-carrot-comfortable",
        "message": "당근이 냉장 보관 중이에요.",
        "is_read": False,
    },
    {
        "user_email": "seed.user3@naenglog.local",
        "ingredient_key": "user3-rice-incorrect-entry",
        "message": "즉석밥 등록 정보를 확인해주세요.",
        "is_read": True,
    },
]
