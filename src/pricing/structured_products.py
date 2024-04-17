from typing import Dict, Optional, Union
from src.pricing.base.option_base import OptionBase
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
        converse_rate: Optional[float] = 0.0,
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

    def decomposition(self) -> Dict[str, Union[OptionBase, ZeroCouponBond]]:
        bond = ZeroCouponBond(self.__rate, self.__maturity, self.__nominal)
        option = VanillaOption(
            self.__spot_price,
            self.__strike_price,
            self.__maturity,
            self.__rate,
            self.__volatility,
            "put",
            self.__dividend,
        )

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
            "rho": (1 - self.__converse_rate) * option.compute_rho(),
            "vega": -(1 - self.__converse_rate) * option.compute_vega(),
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
        foreign_rate: Optional[Rate] = None,
    ) -> None:
        super().__init__("outperformer-certificate")
        if participation <= 1.0:
            raise ValueError(
                "Participation must be greater than 100% (1.0 in decimal form)."
            )

        self.__rate = rate
        self.__maturity = maturity
        self.__spot_price = spot_price
        self.__volatility = volatility
        self.__participation = participation
        self.__dividend = dividend
        self.__foreign_rate = foreign_rate

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

        return self.__spot_price + (1 - self.__participation) * atm_call.compute_price()

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
            "delta": 1 + (1 - self.__participation) * atm_call.compute_delta(),
            "gamma": (1 - self.__participation) * atm_call.compute_gamma(),
            "theta": (1 - self.__participation) * atm_call.compute_theta(),
            "rho": (1 - self.__participation) * atm_call.compute_rho(),
            "vega": (1 - self.__participation) * atm_call.compute_vega(),
        }
