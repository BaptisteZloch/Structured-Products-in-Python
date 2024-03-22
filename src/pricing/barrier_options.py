import numpy as np
from scipy.stats import norm
from src.pricing.base.option_base import OptionBase
from src.pricing.base.rate import Rate
from src.pricing.base.volatility import Volatility
from src.utility.types import Maturity, OptionType, BarrierType


class BarrierOption(OptionBase):
    def __init__(
        self,
        spot_price: float,
        strike_price: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
        option_type: OptionType,
        barrier_level: float,
        barrier_type: BarrierType,
    ) -> None:
        """_summary_

        Args:
            spot_price (float): _description_
            strike_price (float): _description_
            maturity (Maturity): _description_
            rate (Rate): _description_
            volatility (Volatility): The volatility object for the implied vol
            option_type (OptionType): The option type call or put
            barrier_level (float): The barrier level in spot unit.
            barrier_type (BarrierType): The barrier type : KO or KI.
        """
        super().__init__(
            spot_price, strike_price, maturity, rate, volatility, option_type
        )
        self._barrier_level = barrier_level
        self._barrier_type = barrier_type

    def compute_price(self) -> float:
        if self._option_type == "call" and self._barrier_type == "KO":
            # Implement here
            pass
        elif self._option_type == "call" and self._barrier_type == "KI":
            # Implement here
            pass
        elif self._option_type == "put" and self._barrier_type == "KO":
            # Implement here
            pass
        elif self._option_type == "put" and self._barrier_type == "KI":
            # Implement here
            pass
        else:
            raise ValueError("Option type or barrier type not supported.")

    def compute_greeks(self):
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }
