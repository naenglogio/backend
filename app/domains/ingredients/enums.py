from enum import StrEnum


class DeletionReason(StrEnum):
    """ingredients soft delete 사유. is_deleted=true일 때만 값을 가진다."""

    CONSUMED = "CONSUMED"
    DISCARDED = "DISCARDED"
    WRONG_ENTRY = "WRONG_ENTRY"
