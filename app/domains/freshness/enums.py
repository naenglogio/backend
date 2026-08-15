from enum import StrEnum


class StorageType(StrEnum):
    """보관 방식(문자열). product_freshness_profiles가 사용한다.

    BE-1 주의:
    - ingredients.storage_type은 노션 ERD 정본대로 int(0=냉장, 1=냉동)다.
    - 이 문자열 enum은 freshness 프로필 쪽만 계속 쓴다.
    - ROOM_TEMPERATURE는 ingredients에서는 제거됐지만, 프로필 테이블에는 아직 남아 있다.
    """

    REFRIGERATED = "REFRIGERATED"
    FROZEN = "FROZEN"
    ROOM_TEMPERATURE = "ROOM_TEMPERATURE"


class ExpirationSource(StrEnum):
    """소비기한 값의 출처. 05_mvp_models_and_migration.md에서 확정된 값."""

    USER_INPUT = "USER_INPUT"
    PACKAGE_OCR = "PACKAGE_OCR"
    PRODUCT_DISCLOSURE = "PRODUCT_DISCLOSURE"
    MFDS_REFERENCE = "MFDS_REFERENCE"


class ExpirationStatus(StrEnum):
    """소비기한 값의 신뢰도 상태. 05_mvp_models_and_migration.md에서 확정된 값."""

    CONFIRMED = "CONFIRMED"
    ESTIMATED = "ESTIMATED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
