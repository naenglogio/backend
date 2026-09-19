import pytest
from app.domains.freshness import service
from app.domains.freshness.enums import ExpirationSource


@pytest.mark.parametrize(
    ("raw_source", "expected"),
    [
        ("KURLY", ExpirationSource.PRODUCT_DISCLOSURE),
        ("MFDS", ExpirationSource.MFDS_REFERENCE),
        ("MANUAL", ExpirationSource.USER_INPUT),
        ("unknown-value", ExpirationSource.PRODUCT_DISCLOSURE),
    ],
)
def test_map_expiration_source(raw_source: str, expected: ExpirationSource) -> None:
    assert service._map_expiration_source(raw_source) == expected


@pytest.mark.parametrize(
    ("value", "unit", "expected_days"),
    [
        (7, "DAY", 7),
        (2, "WEEK", 14),
        (6, "MONTH", 180),
        (1, "YEAR", 365),
        (24, "HOUR", 1),
        (12, "HOUR", 1),  # 올림 처리 - 0일로 내려가 '이미 지남'처럼 보이지 않게 한다.
        (25, "HOUR", 2),
    ],
)
def test_map_expiration_days(value: int, unit: str, expected_days: int) -> None:
    assert service._map_expiration_days(value, unit) == expected_days


def test_map_expiration_days_rejects_unsupported_unit() -> None:
    with pytest.raises(ValueError, match="지원하지 않는 expiration_unit"):
        service._map_expiration_days(1, "FORTNIGHT")
