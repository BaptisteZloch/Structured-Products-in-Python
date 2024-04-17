from typing import Dict, Optional
from src.pricing.base.rate import Rate
from src.pricing.base.volatility import Volatility
from src.utility.types import Maturity, OptionType
from src.pricing.base.structured_products_base import StructuredProductBase
from src.pricing.vanilla_options import VanillaOption
from src.pricing.fixed_income import ZeroCouponBond
import math as m
import numpy as np


class ReverseConvertible(StructuredProductBase):
    def __init__(
        self,
        rate: Rate,
        maturity: Maturity,
        spot_price: float,
        volatility: Volatility,
        coupon: float,
        dividend: Optional[float] = None,
    ) -> None:
        super().__init__("reverse-convertible")
        self.rate = rate
        self.maturity = maturity
        self.spot_price = spot_price
        self.volatility = volatility
        self.coupon = coupon
        self.dividend = dividend if dividend is not None else 0.0

    def compute_price(self) -> float:

        bond = ZeroCouponBond(self.rate, self.maturity, 100)  
        option = VanillaOption(
            self.spot_price, 
            self.spot_price, 
            self.maturity, 
            self.rate, 
            self.volatility, 
            "put",  
            self.dividend
        )


        discount_factor = np.exp(-self.rate.get_rate(self.maturity) * self.maturity.maturity_in_years)
        discounted_coupon = (self.coupon * discount_factor)*100

        price = (
            bond.compute_price() - 
            option.compute_price() + 
            discounted_coupon
        )

        return price

    def compute_greeks(self) -> Dict[str, float]:

        option = VanillaOption(
            self.spot_price,
            self.spot_price, 
            self.maturity, 
            self.rate, 
            self.volatility, 
            "put",  
            self.dividend
        )


        return {
            "delta": option.compute_delta(),
            "gamma": option.compute_gamma(),
            "theta": option.compute_theta(),
            "rho": option.compute_rho(),
            "vega": option.compute_vega(),
        }


class OutperformerCertificate(StructuredProductBase):
    def __init__(
        self,
        rate: Rate,
        maturity: Maturity,
        spot_price: float,
        volatility: Volatility,
        participation: float,
        dividend: Optional[float] = None,
    ) -> None:
        super().__init__("outperformer-certificate")
        if participation <= 1.0:
            raise ValueError("Participation must be greater than 100% (1.0 in decimal form).")
        
        self.__rate = rate
        self.__maturity = maturity
        self.__spot_price = spot_price
        self.__volatility = volatility
        self.__participation = participation
        self.__dividend = dividend

    def compute_price(self) -> float:
        atm_call = VanillaOption(
            self.__spot_price,
            self.__spot_price, 
            self.__maturity,
            self.__rate,
            self.__volatility,
            "call",
            self.__dividend,
        )

        print(m.exp(-self.__dividend* self.__maturity.maturity_in_years) * self.__spot_price)
        print((self.__participation - 1) * atm_call.compute_price())
        return m.exp(-self.__dividend* self.__maturity.maturity_in_years) * self.__spot_price + (self.__participation - 1) * atm_call.compute_price()

    def compute_greeks(self, eps: Optional[float] = 0.01) -> Dict[str, float]:
        atm_call = VanillaOption(
            self.__spot_price,
            self.__spot_price,
            self.__maturity,
            self.__rate,
            self.__volatility,
            "call",
            self.__dividend,
        )

        return {
            "delta": 1 + (self.__participation - 1) * atm_call.compute_delta(),
            "gamma": (self.__participation - 1) * atm_call.compute_gamma(),
            "theta": (self.__participation - 1) * atm_call.compute_theta(),
            "rho": (self.__participation - 1) * atm_call.compute_rho(),
            "vega": (self.__participation - 1) * atm_call.compute_vega(),
        }
