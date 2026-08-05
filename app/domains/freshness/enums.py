from enum import StrEnum


class StorageType(StrEnum):
    """식재료 보관 방식. ingredients와 product_freshness_profiles가 공유하는 값이다."""

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
