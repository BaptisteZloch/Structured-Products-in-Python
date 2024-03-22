import numpy as np
from scipy.stats import norm
from src.pricing.base.option_base import OptionBase
from src.pricing.base.rate import Rate
from src.pricing.base.volatility import Volatility
from src.utility.types import Maturity, OptionType


class BinaryOption(OptionBase):
    def __init__(
        self,
        spot_price: float,
        strike_price: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
        option_type: OptionType,
    ) -> None:
        super().__init__(
            spot_price, strike_price, maturity, rate, volatility, option_type
        )

    def compute_price(self) -> float:
        if self._option_type == "call":
            return np.exp(
                -self._rate.get_rate(self._maturity) * self._maturity.maturity_in_years
            ) * norm.cdf(self._d2)
        elif self._option_type == "put":
            return np.exp(
                -self._rate.get_rate(self._maturity) * self._maturity.maturity_in_years
            ) * norm.cdf(-self._d2)
        else:
            raise ValueError("Option type not supported. Use 'call' or 'put'.")

    def compute_greeks(self):
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }
