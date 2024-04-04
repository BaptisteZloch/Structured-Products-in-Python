from typing import Dict, Optional
from src.pricing.base.structured_products_base import StructuredProductBase
from src.pricing.base.volatility import Volatility
from src.pricing.fixed_income import ZeroCouponBond
from src.pricing.vanilla_options import VanillaOption
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
        converse_rate: float,
        dividend: Optional[float] = None,
    ) -> None:
        super().__init__("reverse-convertible")
        self.__rate = rate
        self.__maturity = maturity
        self.__nominal = nominal
        self.__spot_price = spot_price
        self.__strike_price = strike_price
        self.__volatility = volatility
        self.__converse_rate = converse_rate
        self.__dividend = dividend

    def decomposition(self) -> Dict:
        bond = ZeroCouponBond(self.__rate, self.__maturity, self.__nominal)
        option = VanillaOption(
            self.__spot_price, 
            self.__strike_price, 
            self.__maturity, 
            self.__rate, self.__volatility, 
            "put", 
            self.__dividend)

        return {"bond": bond, "option": option}

    def compute_price(self) -> float:
        dico = self.decomposition()
        option = dico["option"]
        bond = dico["bond"]

        self._price = (
            bond.compute_price() - (1 - self.__converse_rate) * option.compute_price()
        )

        return self._price

    def compute_greeks(self) -> Dict[str, float]:
        dico = self.decomposition()
        option = dico["option"]
        bond = dico["bond"]
        return {
            "delta": -(1 - self.__converse_rate) * option.compute_delta(),
            "gamma": -(1 - self.__converse_rate) * option.compute_gamma(),
            "theta": -(1 - self.__converse_rate) * option.compute_theta(),
            "rho": -(1 - self.__converse_rate) * option.compute_rho(),
            "vega": -(1 - self.__converse_rate) * option.compute_vega(),
        }

class OutperformerCertificate(StructuredProductBase):
    def __init__(
        self,
        rate: Rate,
        maturity: Maturity,
        spot_price: float,
        strike_price: float,
        volatility: Volatility,
        participation: float,
        dividend: Optional[float] = None,
        foreign_rate: Optional[Rate] = None,
    ) -> None:
        super().__init__("outperformer-certificate")
        self.__rate = rate
        self.__maturity = maturity
        self.__spot_price = spot_price
        self.__strike_price = strike_price
        self.__volatility = volatility
        if participation < 1:
            raise ValueError("Participation must be higher than 100%")
        self.__participation = participation
        self.__dividend = dividend
        self.__foreign_rate = foreign_rate

    def decomposition(self, atm: Optional[bool] = False) -> Dict:
        option_call1 = VanillaOption(
            self.__spot_price,
            0,
            self.__maturity,
            self.__rate,
            self.__volatility,
            "call",
            self.__dividend,
            self.__foreign_rate,
        )
        
        spot = (1-atm)*self.__spot_price + atm*self.__strike_price
        
        option_call2 = VanillaOption(
            spot,
            self.__strike_price,
            self.__maturity,
            self.__rate,
            self.__volatility,
            "call",
            self.__dividend,
            self.__foreign_rate,
        )

        return {
            "option_call1": option_call1,
            "option_call2": option_call2
        }

    def compute_price(self) -> float:
        dico = self.decomposition(atm=True)

        self._price = (
            dico["option_call1"].compute_price()
            + (self.__participation-1) * dico["option_call2"].compute_price()
        )
        return self._price

    def compute_greeks(self) -> Dict[str, float]:
        dico = self.decomposition()
        OC1 = dico["option_call1"]
        OC2 = dico["option_call2"]
        return {
            "delta": OC1.compute_delta() + (self.__participation-1) *  OC2.compute_delta(),
            "gamma": OC1.compute_gamma() + (self.__participation-1) * OC2.compute_gamma(),
            "theta": OC1.compute_theta() + (self.__participation-1) * OC2.compute_theta(),
            "rho": OC1.compute_rho() + (self.__participation-1) * OC2.compute_rho(),
            "vega": OC1.compute_vega() + (self.__participation-1) * OC2.compute_vega(),
        }
