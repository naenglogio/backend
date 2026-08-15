from enum import StrEnum


class DeletionReason(StrEnum):
    """ingredients soft delete 사유. is_deleted=true일 때만 값을 가진다.

    BE-1: 노션 ERD 정본에 맞춰 WRONG_ENTRY → INCORRECT_ENTRY로 변경.
    """

    CONSUMED = "CONSUMED"  # 소비(먹음)
    DISCARDED = "DISCARDED"  # 폐기(버림)
    INCORRECT_ENTRY = "INCORRECT_ENTRY"  # 잘못된 등록 취소
