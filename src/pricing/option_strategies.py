from abc import ABC, abstractmethod
from pricing.base.rate import Rate
from pricing.base.volatility import Volatility
from pricing.vanilla_options import VanillaOption
from utility.types import Maturity


class OptionStrategy(ABC):
    def __init__(
        self,
        spot_price: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
    ) -> None:
        self._spot_price = spot_price
        self._maturity = maturity
        self._rate = rate
        self._volatility = volatility

    @abstractmethod
    def compute_price(self):
        pass


class StraddleStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        strike_price: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility)
        self._strike_price = strike_price

    def compute_price(self) -> float:
        return (
            VanillaOption(
                self._spot_price,
                self._strike_price,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
            ).compute_price()
            + VanillaOption(
                self._spot_price,
                self._strike_price,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
            ).compute_price()
        )


class StrangleStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        strike_price1: float,
        strike_price2: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
    ) -> None:
        """_summary_

        Args:
            spot_price (float): _description_
            strike_price1 (float): The lower strike price K1.
            strike_price2 (float): The upper strike price K2.
            maturity (Maturity): The maturity object representing the Maturity of the options.
            rate (Rate): _description_
            volatility (Volatility): _description_
        """
        super().__init__(spot_price, maturity, rate, volatility)
        assert (
            strike_price1 < strike_price2
        ), "Error provide strike_price1 < strike_price2."
        self._strike_price1 = strike_price1
        self._strike_price2 = strike_price2

    def compute_price(self) -> float:
        return (
            VanillaOption(
                self._spot_price,
                self._strike_price2,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
            ).compute_price()
            + VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
            ).compute_price()
        )


class ButterflyStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        strike_price1: float,
        strike_price2: float,
        strike_price3: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility)
        assert (
            strike_price1 < strike_price2 < strike_price3
        ), "Error provide strike_price1 < strike_price2 < strike_price3."
        self._strike_price1 = strike_price1
        self._strike_price2 = strike_price2
        self._strike_price3 = strike_price3

    def compute_price(self) -> float:
        return (
            VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
            ).compute_price()
            - 2 * VanillaOption(
                self._spot_price,
                self._strike_price2,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
            ).compute_price()
            + VanillaOption(
                self._spot_price,
                self._strike_price3,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
            ).compute_price()
        )


class CallSpreadStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        lower_strike: float,
        upper_strike: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility)
        assert (
            lower_strike < upper_strike
        ), "Error: lower strike must be less than upper strike."
        self._lower_strike = lower_strike
        self._upper_strike = upper_strike

    def compute_price(self) -> float:
        return (
            VanillaOption(
                self._spot_price,
                self._lower_strike,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
            ).compute_price()
            - VanillaOption(
                self._spot_price,
                self._upper_strike,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
            ).compute_price()
        )


class PutSpreadStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        lower_strike: float,
        upper_strike: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility)
        assert (
            lower_strike < upper_strike
        ), "Error: lower strike must be less than upper strike."
        self._lower_strike = lower_strike
        self._upper_strike = upper_strike

    def compute_price(self) -> float:
        return (
            VanillaOption(
                self._spot_price,
                self._upper_strike,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
            ).compute_price()
            - VanillaOption(
                self._spot_price,
                self._lower_strike,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
            ).compute_price()
        )


class StripStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        strike_price1: float,
        strike_price2: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility)
        assert (
            strike_price1 < strike_price2
        ), "Error provide strike_price1 < strike_price2."
        self._strike_price1 = strike_price1
        self._strike_price2 = strike_price2

    def compute_price(self) -> float:
        return (
            2 * VanillaOption(
                self._spot_price,
                self._strike_price2,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
            ).compute_price()
            - VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
            ).compute_price()
        )


class StrapStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        strike_price1: float,
        strike_price2: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility)
        assert (
            strike_price1 < strike_price2
        ), "Error provide strike_price1 < strike_price2."
        self._strike_price1 = strike_price1
        self._strike_price2 = strike_price2

    def compute_price(self) -> float:
        return (
            VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
            ).compute_price()
            - 2 * VanillaOption(
                self._spot_price,
                self._strike_price2,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
            ).compute_price()
        )
