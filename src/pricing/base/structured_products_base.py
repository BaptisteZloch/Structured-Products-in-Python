from abc import ABC, abstractmethod


class StructuredProductBase(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def compute_price(self):
        pass

    @abstractmethod
    def compute_greeks(self):
        pass
