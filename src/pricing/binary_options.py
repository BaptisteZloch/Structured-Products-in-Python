from pricing.base.option_base import OptionBase
from pricing.base.rate import Rate
from pricing.base.volatility import Volatility
from utility.types import Maturity, OptionType


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

    def compute_option_price(self):
        raise NotImplementedError()
