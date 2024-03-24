from abc import ABC, abstractmethod
from src.utility.types import ProductKindType
from typing import Optional

class StructuredProductBase(ABC):
    _price: Optional[float] = None
    
    def __init__(
            self,
            product_type: ProductKindType
    ) -> None:
        self.__product_type = product_type

    @abstractmethod
    def compute_price(self):
        pass

    @abstractmethod
    def compute_greeks(self):
        pass


