from enum import StrEnum


class ProductSource(StrEnum):
    """상품 식별 출처. 컬리/N마트 외 출처가 늘어나면 여기에 추가한다."""

    KURLY = "KURLY"
    N_MART = "N_MART"
