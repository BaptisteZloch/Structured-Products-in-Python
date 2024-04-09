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
                self._foreign_rate,
            ).compute_price()
        )
    def compute_greeks(self):
        call_option = VanillaOption(
            self._spot_price,
            self._strike_price,
            self._maturity,
            self._rate,
            self._volatility,
            "call",
            self._dividend,
            self._foreign_rate,
        )
        put_option = VanillaOption(
            self._spot_price,
            self._strike_price,
            self._maturity,
            self._rate,
            self._volatility,
            "put",
            self._dividend,
            self._foreign_rate,
        )

        call_greeks = call_option.compute_greeks()
        put_greeks = put_option.compute_greeks()

        combined_greeks = {
            greek: call_greeks[greek] + put_greeks[greek] for greek in call_greeks
        }
        
        return combined_greeks

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
        lower_strike_call = VanillaOption(
            self._spot_price,
            self._strike_price1,
            self._maturity,
            self._rate,
            self._volatility,
            "call",
            self._dividend,
            self._foreign_rate,
        )
        higher_strike_put = VanillaOption(
            self._spot_price,
            self._strike_price2,
            self._maturity,
            self._rate,
            self._volatility,
            "put",
            self._dividend,
            self._foreign_rate,
        )

        call_greeks = lower_strike_call.compute_greeks()
        put_greeks = higher_strike_put.compute_greeks()

        combined_greeks = {
            greek: call_greeks[greek] + put_greeks[greek] for greek in call_greeks
        }
        
        return combined_greeks


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
            long_call_low = VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
                self._foreign_rate,
            )
            short_call_mid = VanillaOption(
                self._spot_price,
                self._strike_price2,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
                self._foreign_rate,
            )
            long_call_high = VanillaOption(
                self._spot_price,
                self._strike_price3,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
                self._foreign_rate,
            )

            low_greeks = long_call_low.compute_greeks()
            mid_greeks = short_call_mid.compute_greeks()
            high_greeks = long_call_high.compute_greeks()

            combined_greeks = {
                greek: low_greeks[greek] - 2 * mid_greeks[greek] + high_greeks[greek] for greek in low_greeks
            }
            
            return combined_greeks


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
                option_type="call",
                dividend=self._dividend,
                foreign_rate=self._foreign_rate,
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
        long_call = VanillaOption(
            self._spot_price,
            self._lower_strike,
            self._maturity,
            self._rate,
            self._volatility,
            "call",
            self._dividend,
            self._foreign_rate,
        )
        short_call = VanillaOption(
            self._spot_price,
            self._upper_strike,
            self._maturity,
            self._rate,
            self._volatility,
            "call",
            self._dividend,
            self._foreign_rate,
        )

        long_call_greeks = long_call.compute_greeks()
        short_call_greeks = short_call.compute_greeks()

        combined_greeks = {
            greek: long_call_greeks[greek] - short_call_greeks[greek] for greek in long_call_greeks
        }
        
        return combined_greeks

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
        long_put = VanillaOption(
            self._spot_price,
            self._upper_strike,
            self._maturity,
            self._rate,
            self._volatility,
            "put",
            self._dividend,
            self._foreign_rate,
        )
        short_put = VanillaOption(
            self._spot_price,
            self._lower_strike,
            self._maturity,
            self._rate,
            self._volatility,
            "put",
            self._dividend,
            self._foreign_rate,
        )

        long_put_greeks = long_put.compute_greeks()
        short_put_greeks = short_put.compute_greeks()

        combined_greeks = {
            greek: long_put_greeks[greek] - short_put_greeks[greek] for greek in long_put_greeks
        }
        
        return combined_greeks


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
                maturity=self._maturity,
                rate=self._rate,
                dividend=self._dividend,
                volatility=self._volatility,
                foreign_rate=self._foreign_rate,
                option_type="put",
            ).compute_price()
            - VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                rate=self._rate,
                volatility=self._volatility,
                option_type="put",
                dividend=self._dividend,
                foreign_rate=self._foreign_rate,
            ).compute_price()
        )

    def compute_greeks(self):
    
            call_option = VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
                self._foreign_rate,
            )
            put_option1 = VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
                self._dividend,
                self._foreign_rate,
            )
            put_option2 = VanillaOption(
                self._spot_price,
                self._strike_price2,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
                self._dividend,
                self._foreign_rate,
            )

            call_greeks = call_option.compute_greeks()
            put_greeks1 = put_option1.compute_greeks()
            put_greeks2 = put_option2.compute_greeks()

            combined_greeks = {
                greek: call_greeks[greek] + put_greeks1[greek] + put_greeks2[greek] for greek in call_greeks
            }
            
            return combined_greeks

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
            call_option1 = VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
                self._foreign_rate,
            )
            call_option2 = VanillaOption(
                self._spot_price,
                self._strike_price2,
                self._maturity,
                self._rate,
                self._volatility,
                "call",
                self._dividend,
                self._foreign_rate,
            )
            put_option = VanillaOption(
                self._spot_price,
                self._strike_price1,
                self._maturity,
                self._rate,
                self._volatility,
                "put",
                self._dividend,
                self._foreign_rate,
            )

            call_greeks1 = call_option1.compute_greeks()
            call_greeks2 = call_option2.compute_greeks()
            put_greeks = put_option.compute_greeks()

            combined_greeks = {
                greek: call_greeks1[greek] + call_greeks2[greek] + put_greeks[greek] for greek in call_greeks1
            }
            
            return combined_greeks