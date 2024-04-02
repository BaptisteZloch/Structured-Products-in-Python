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
        option = BinaryOption(
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

    def compute_greeks(self, eps: Optional[float] = 0.01) -> Dict[str, float]:
        dico = self.decomposition()
        option = dico["option"]
        bond = dico["bond"]
        return {
            "delta": -(1 - self.__converse_rate) * option.compute_delta(),
            "gamma": -(1 - self.__converse_rate) * option.compute_gamma(),
            "theta": -(1 - self.__converse_rate) * option.compute_theta(),
            # "rho": bond.compute_rho(eps)
            # - (1 - self.__converse_rate) * option.compute_rho(),
            "rho": (1 - self.__converse_rate) * option.compute_rho(),
            "vega": -(1 - self.__converse_rate) * option.compute_vega(),
        }


class OutperformerCertificate(StructuredProductBase):
    def __init__(
        self,
        rate: Rate,
        maturity1: Maturity,
        maturity2: Maturity,
        nominal: int,
        spot_price: float,
        strike_price1: float,
        strike_price2: float,
        volatility: Volatility,
        n_call: float,
        dividend: Optional[float] = None,
    ) -> None:
        super().__init__("outperformer-certificate")
        self.__rate = rate
        self.__maturity1 = maturity1
        self.__maturity2 = maturity2
        self.__nominal = nominal
        self.__spot_price = spot_price
        self.__strike_price1 = strike_price1
        self.__strike_price2 = strike_price2
        self.__volatility = volatility
        self.__n_call = n_call
        self.__dividend = dividend

    def decomposition(self) -> Dict:
        bond = ZeroCouponBond(self.__rate, self.__maturity1, self.__nominal)
        option_call1 = BinaryOption(
            self.__spot_price,
            self.__strike_price1,
            self.__maturity2,
            self.__rate,
            self.__volatility,
            "call",
            self.__dividend,
        )
        option_call2 = BinaryOption(
            self.__spot_price,
            self.__strike_price2,
            self.__maturity2,
            self.__rate,
            self.__volatility,
            "call",
            self.__dividend,
        )
        option_put = BinaryOption(
            self.__spot_price,
            self.__strike_price1,
            self.__maturity2,
            self.__rate,
            self.__volatility,
            "put",
            self.__dividend,
        )

        return {
            "bond": bond,
            "option_call1": option_call1,
            "option_call2": option_call2,
            "option_put": option_put,
        }

    def compute_price(self) -> float:
        dico = self.decomposition()
        n = self.__n_call

        self._price = (
            dico["bond"].compute_price()
            + n * dico["option_call1"].compute_price()
            - n * dico["option_call2"].compute_price()
            - dico["option_put"].compute_price()
        )
        return self._price

    def compute_greeks(self, eps: Optional[float] = 0.01) -> Dict[str, float]:
        dico = self.decomposition()
        bond: ZeroCouponBond = dico["bond"]
        OC1 = dico["option_call1"]
        OC2 = dico["option_call2"]
        OP: BinaryOption = dico["option_put"]
        n = self.__n_call
        return {
            "delta": n * (OC1.compute_delta() - OC2.compute_delta())
            - OP.compute_delta(),
            "gamma": n * (OC1.compute_gamma() - OC2.compute_gamma())
            - OP.compute_gamma(),
            "theta": n * (OC1.compute_theta() - OC2.compute_theta())
            - OP.compute_theta(),
            # "rho": bond.compute_rho(eps)
            # + n * (OC1.compute_rho() - OC2.compute_rho())
            # - OP.compute_rho(),
            "rho": n * (OC1.compute_rho() - OC2.compute_rho()) - OP.compute_rho(),
            "vega": n * (OC1.compute_vega() - OC2.compute_vega()) - OP.compute_vega(),
        }
