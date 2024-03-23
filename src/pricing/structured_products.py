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
        
        self._price = bond.compute_price() - (1-self.__converse_rate) * option.compute_price()
        
        return self._price


    def compute_greeks(self) -> Dict[str, float]:
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }


class OutperformerCertificate(StructuredProductBase):
    
    def __init__(
        self,
        rate: Rate,
        maturity: Maturity,
        nominal: int,
        spot_price: float,
        strike_price1: float,
        strike_price2: float,
        volatility: Volatility,
        n_call: float,
    ) -> None:
        super().__init__("outperformer-certificate")
        self.__rate = rate
        self.__maturity = maturity
        self.__nominal = nominal
        self.__spot_price = spot_price
        self.__strike_price1 = strike_price1
        self.__strike_price2 = strike_price2
        self.__volatility = volatility
        self.__n_call = n_call
        
        
    def compute_price(self) -> float:
        mat = Maturity(maturity_in_years=1)
        bond = ZeroCouponBond(
            self.__rate, 
            self.__maturity, 
            self.__nominal
            )
        option_call1 = BinaryOption(
            self.__spot_price, 
            self.__strike_price1, 
            mat, 
            self.__rate, 
            self.__volatility,
            "call"
            )
        option_call2 = BinaryOption(
            self.__spot_price, 
            self.__strike_price2, 
            mat, 
            self.__rate, 
            self.__volatility,
            "call"
            )
        option_put = BinaryOption(
            self.__spot_price, 
            self.__strike_price1, 
            mat, 
            self.__rate, 
            self.__volatility,
            "put"
            )
        self._price = bond.compute_price() \
                    + self.__n_call * option_call1.compute_price() \
                    - self.__n_call * option_call2.compute_price() \
                    - option_put.compute_price()
        return self._price

    def compute_greeks(self) -> Dict[str, float]:
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }
