import numpy as np
from scipy.stats import norm
from pricing.base.option_base import OptionBase
from pricing.base.volatility import Volatility
from pricing.base.rate import Rate
from utility.types import OptionType, Maturity


class VanillaOption(OptionBase):
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

    def compute_option_price(self):
        if self._option_type == "call":
            return self._spot_price * norm.cdf(self._d1) - self._strike_price * np.exp(
                -self._rate.get_rate() * self._maturity.maturity_in_years
            ) * norm.cdf(self._d2)
        elif self._option_type == "put":
            return self._strike_price * np.exp(
                -self._rate.get_rate() * self._maturity.maturity_in_years
            ) * norm.cdf(-self._d2) - self._spot_price * norm.cdf(-self._d1)
        else:
            raise ValueError("Option type not supported. Use 'call' or 'put'.")
