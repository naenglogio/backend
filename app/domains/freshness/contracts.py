"""데이터 파이프라인이 넘겨주는 '정제 완료 결과'의 계약.

07_mock_and_seed_data.md에 실린 예시 JSON을 그대로 반영한다. 실제 계약이 별도
문서로 확정되면 그 문서를 우선하고 이 dataclass를 맞춰 수정한다.

원문 OCR JSON이나 정제 중간 산출물은 여기 담지 않는다 — 최종 필드만 받는다.
"""

from dataclasses import dataclass

from app.domains.products.enums import ProductSource


@dataclass(frozen=True, slots=True)
class RefinedFreshnessRecord:
    external_product_id: str
    product_name: str
    food_name: str
    storage_type: str
    expiration_value: int
    expiration_unit: str
    expiration_basis: str
    source: str
    confidence: float
    review_status: str
    # 예시 계약 JSON에는 없지만, products.source(KURLY/N_MART) 유니크 제약을 채우려면
    # 상품이 어느 마켓 출신인지 알아야 한다. 실제 계약이 확정되면 이 필드를 계약에
    # 포함시키거나, 파이프라인이 별도 채널로 마켓 구분을 제공하는 방식으로 대체한다.
    product_source: ProductSource
