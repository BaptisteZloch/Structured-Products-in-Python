from abc import ABC, abstractmethod
from typing import Optional
from src.pricing.base.rate import Rate
from src.pricing.base.volatility import Volatility
from src.pricing.vanilla_options import VanillaOption
from src.utility.types import Maturity


class OptionStrategy(ABC):
    def __init__(
        self,
        spot_price: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
        dividend: Optional[float] = None,
        foreign_rate: Optional[Rate] = None, 
    ) -> None:
        self._spot_price = spot_price
        self._maturity = maturity
        self._rate = rate
        self._volatility = volatility
        self._dividend = dividend if dividend is not None else 0.0
        self._foreign_rate = foreign_rate  

    @abstractmethod
    def compute_greeks(self):
        pass


class StraddleStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        strike_price: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
        dividend: Optional[float] = None,
        foreign_rate: Optional[Rate] = None, 

    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility, dividend, foreign_rate)
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
                self._dividend,
                self._foreign_rate,
            ).compute_price()
            + VanillaOption(
                self._spot_price,
                self._strike_price,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
                self._foreign_rate
            ).compute_price()
        )

    def compute_greeks(self):
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }


class StrangleStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        strike_price1: float,
        strike_price2: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
        dividend: Optional[float] = None,
        foreign_rate: Optional[Rate] = None, 
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
        super().__init__(spot_price, maturity, rate, volatility, dividend, foreign_rate)
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
                self._dividend,
                self._foreign_rate,
            ).compute_price()
            + VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
                self._foreign_rate,
            ).compute_price()
        )

    def compute_greeks(self):
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }


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
        dividend: Optional[float] = None,
        foreign_rate: Optional[Rate] = None, 
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility, dividend, foreign_rate)
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
                self._dividend,
                self._foreign_rate,
            ).compute_price()
            - 2
            * VanillaOption(
                self._spot_price,
                self._strike_price2,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
            ).compute_price()
            + VanillaOption(
                self._spot_price,
                self._strike_price3,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
                self._foreign_rate,
            ).compute_price()
        )

    def compute_greeks(self):
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }


class CallSpreadStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        lower_strike: float,
        upper_strike: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
        dividend: Optional[float] = None,
        foreign_rate: Optional[Rate] = None, 
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility, dividend, foreign_rate)
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
                self._dividend,
                self._foreign_rate,
            ).compute_price()
            - VanillaOption(
                self._spot_price,
                self._upper_strike,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
                self._foreign_rate,
            ).compute_price()
        )

    def compute_greeks(self):
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }


class PutSpreadStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        lower_strike: float,
        upper_strike: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
        dividend: Optional[float] = None,
        foreign_rate: Optional[Rate] = None, 
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility, dividend, foreign_rate)
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
                self._dividend,
                self._foreign_rate,
            ).compute_price()
            - VanillaOption(
                self._spot_price,
                self._lower_strike,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
                self._dividend,
                self._foreign_rate,
            ).compute_price()
        )

    def compute_greeks(self):
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }


class StripStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        strike_price1: float,
        strike_price2: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
        dividend: Optional[float] = None,
        foreign_rate: Optional[Rate] = None, 
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility, dividend, foreign_rate)
        assert (
            strike_price1 < strike_price2
        ), "Error provide strike_price1 < strike_price2."
        self._strike_price1 = strike_price1
        self._strike_price2 = strike_price2

    def compute_price(self) -> float:
        return (
            2
            * VanillaOption(
                self._spot_price,
                self._strike_price2,
                self._maturity,
                self._rate,
                self._volatility,
                self._foreign_rate,
                "put",
            ).compute_price()
            - VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
                self._dividend,
                self._foreign_rate,
            ).compute_price()
        )

    def compute_greeks(self):
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }


class StrapStrategy(OptionStrategy):
    def __init__(
        self,
        spot_price: float,
        strike_price1: float,
        strike_price2: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
        dividend: Optional[float] = None,
        foreign_rate: Optional[Rate] = None,
    ) -> None:
        super().__init__(spot_price, maturity, rate, volatility, dividend, foreign_rate)
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
                self._dividend,
                self._foreign_rate,
            ).compute_price()
            - 2
            * VanillaOption(
                self._spot_price,
                self._strike_price2,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
                self._dividend,
                self._foreign_rate,
            ).compute_price()
        )

    def compute_greeks(self):
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "rho": 0.0,
            "vega": 0.0,
        }
