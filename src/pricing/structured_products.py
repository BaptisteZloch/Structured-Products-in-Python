from typing import Dict, Optional
from src.pricing.base.structured_products_base import StructuredProductBase
from src.pricing.base.volatility import Volatility
from src.pricing.fixed_income import ZeroCouponBond
from src.pricing.binary_options import BinaryOption
from src.pricing.base.rate import Rate
from src.utility.types import Maturity

class ReverseConvertible(StructuredProductBase):
    
    def __init__(
        self, 
        rate: Rate,
        maturity: Maturity,
        nominal: int,
        spot_price: float,
        strike_price: float,
        volatility: Volatility,
        converse_rate: float
    ) -> None:
        super().__init__("reverse-convertible")
        self.__rate = rate
        self.__maturity = maturity
        self.__nominal = nominal
        self.__spot_price = spot_price
        self.__strike_price = strike_price
        self.__volatility = volatility
        self.__converse_rate = converse_rate


    def compute_price(self) -> float:
        bond = ZeroCouponBond(
            self.__rate, 
            self.__maturity, 
            self.__nominal
            )
        option = BinaryOption(
            self.__spot_price, 
            self.__strike_price, 
            self.__maturity, 
            self.__rate, 
            self.__volatility,
            "put"
            )
        
        self.__price = self.__converse_rate * bond.compute_price() + (1-self.__converse_rate) * option.compute_price()
        
        return self.__price


    def compute_greeks(self) -> Dict[str, float]:
        raise NotImplementedError()


class OutperformerCertificate(StructuredProductBase):
    
    def __init__(
        self,
        
    ) -> None:
        super().__init__("outperformer-certificate")

    def compute_price(self) -> float:
        raise NotImplementedError()

    def compute_greeks(self) -> Dict[str, float]:
        raise NotImplementedError()
