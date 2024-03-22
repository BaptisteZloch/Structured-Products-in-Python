from typing import Dict
from src.pricing.base.structured_products_base import StructuredProductBase


class ReverseConvertible(StructuredProductBase):
    def __init__(self) -> None:
        pass

    def compute_price(self) -> float:
        raise NotImplementedError()

    def compute_greeks(self) -> Dict[str, float]:
        raise NotImplementedError()


class OutperformerCertificate(StructuredProductBase):
    def __init__(self) -> None:
        pass

    def compute_price(self) -> float:
        raise NotImplementedError()

    def compute_greeks(self) -> Dict[str, float]:
        raise NotImplementedError()
