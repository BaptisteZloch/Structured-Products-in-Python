from typing import Optional
import numpy as np
from scipy.stats import norm
from tqdm import tqdm
from src.pricing.base.option_base import OptionBase
from src.pricing.base.rate import Rate
from src.pricing.base.volatility import Volatility
from src.utility.types import BarrierDirection, Maturity, OptionType, BarrierType
from src.utility.constants import EPSILON


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
        barrier_direction: BarrierDirection,
        dividend: Optional[float] = None,
        foreign_rate: Optional[Rate] = None,

    ) -> None:
        super().__init__(
            spot_price, strike_price, maturity, rate, volatility, option_type, dividend, foreign_rate
        )
        self._barrier_level = barrier_level
        self._barrier_type = barrier_type
        self._barrier_direction = barrier_direction

    def compute_price(self, num_paths=20000, num_steps=500) -> float:
        paths = self.monte_carlo_simulation(num_paths=num_paths, num_steps=num_steps)
        payoffs = []

        for path in tqdm(paths, desc="Computing paths...", leave=False):
            barrier_crossed = (
                np.any(path >= self._barrier_level)
                if self._barrier_direction == "up"
                else np.any(path <= self._barrier_level)
            )

            if self._option_type == "call":
                intrinsic_value = max(path[-1] - self._strike_price, 0)
            elif self._option_type == "put":
                intrinsic_value = max(self._strike_price - path[-1], 0)

            if self._barrier_type == "ko":
                payoff = 0 if barrier_crossed else intrinsic_value
            elif self._barrier_type == "ki":
                payoff = intrinsic_value if barrier_crossed else 0

            payoffs.append(payoff)

        average_payoff = np.mean(payoffs)
        effective_rate = self._domestic_rate.get_rate(self._maturity) - (self._foreign_rate.get_rate(self._maturity) if self._foreign_rate else self._dividend)
        discounted_price = np.exp(-effective_rate * self._maturity.maturity_in_years) * average_payoff

        return discounted_price


    def compute_price_variation(
        self, spot_price=None, volatility=None, rate=None, maturity=None
    ):
        original_spot = self._spot_price
        original_volatility = self._volatility.get_volatility()
        original_rate = self._domestic_rate.get_rate(self._maturity) - self._dividend
        original_maturity = self._maturity.maturity_in_years

        if spot_price is not None:
            self._spot_price = spot_price
        if volatility is not None:
            self._volatility = Volatility(volatility)
        if rate is not None:
            self._rate = Rate(rate)
        if maturity is not None:
            self._maturity = Maturity(maturity_in_years=maturity)

        price = self.compute_price()

        self._spot_price = original_spot
        self._volatility = Volatility(original_volatility)
        self._rate = Rate(original_rate)
        self._maturity = Maturity(maturity_in_years=original_maturity)

        return price

    def compute_delta(self):
        price_up = self.compute_price_variation(spot_price=self._spot_price + EPSILON)
        
        price_down = self.compute_price_variation(spot_price=self._spot_price - EPSILON)
        print(price_up)
        print(price_down)
        delta = (price_up - price_down) / 2*EPSILON
        return delta

    def compute_gamma(self):
        price_up = self.compute_price_variation(spot_price=self._spot_price + EPSILON)
        price_down = self.compute_price_variation(spot_price=self._spot_price - EPSILON)
        price = self.compute_price()
        gamma = (price_up - 2 * price + price_down) / (EPSILON**2)
        return gamma

    def compute_vega(self):
        price_up = self.compute_price_variation(
            volatility=self._volatility.get_volatility() + EPSILON
        )
        price_down = self.compute_price_variation(
            volatility=self._volatility.get_volatility() - EPSILON
        )
        vega = (price_up - price_down) / 2* EPSILON
        return vega

    def compute_rho(self):
        price_up = self.compute_price_variation(
            rate=(self._rate.get_rate(self._maturity) - self._dividend) + EPSILON
        )
        price_down = self.compute_price_variation(
            rate=(self._rate.get_rate(self._maturity) - self._dividend) - EPSILON
        )
        rho = (price_up - price_down) / 2* EPSILON
        return rho

    def compute_theta(self):
        day_in_years = 1 / 365
        price_tomorrow = self.compute_price_variation(
            maturity=self._maturity.maturity_in_years + day_in_years
        )
        price_today = self.compute_price()
        theta = (price_tomorrow - price_today) / day_in_years
        return theta

    def compute_greeks(self):
        return {
            "delta": self.compute_delta(),
            "gamma": self.compute_gamma(),
            "theta": self.compute_theta(),
            "vega": self.compute_vega(),
            "rho": self.compute_rho(),
        }
