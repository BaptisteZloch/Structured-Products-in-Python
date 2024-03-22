from abc import ABC, abstractmethod

import numpy as np

from pricing.base.volatility import Volatility
from pricing.base.rate import Rate
from utility.types import OptionType, Maturity


class OptionBase(ABC):
    def __init__(
        self,
        spot_price: float,
        strike_price: float,
        maturity: Maturity,
        rate: Rate,
        volatility: Volatility,
        option_type: OptionType,
    ) -> None:
        self._spot_price = spot_price
        self._strike_price = strike_price
        self._maturity = maturity
        self._rate = rate
        self._volatility = volatility
        self._option_type = option_type

        self._d1 = self.__d1_func()
        self._d2 = self.__d2_func()

    def __d1_func(self) -> float:
        """Compute d1 of the Black-Scholes formula.

        Returns:
            float: The value of d1.
        """
        return (
            np.log(self._spot_price / self._strike_price)
            + (self._rate.get_rate() + 0.5 * self._volatility.get_volatility() ** 2)
            * self._maturity.maturity_in_years
        ) / (
            self._volatility.get_volatility()
            * np.sqrt(self._maturity.maturity_in_years)
        )

    def __d2_func(self) -> float:
        """Compute d2 of the Black-Scholes formula.

        Returns:
            float: The value of d2.
        """

        return (
            np.log(self._spot_price / self._strike_price)
            + (self._rate.get_rate() + 0.5 * self._volatility.get_volatility() ** 2)
            * self._maturity.maturity_in_years
        ) / (
            self._volatility.get_volatility()
            * np.sqrt(self._maturity.maturity_in_years)
        ) - self._volatility.get_volatility() * np.sqrt(
            self._maturity.maturity_in_years
        )

    @property
    def d1(self) -> float:
        return self._d1

    @property
    def d2(self) -> float:
        return self._d2

    @abstractmethod
    def compute_price(self):
        pass
    
    @abstractmethod
    def compute_greeks(self):
        pass
    
    def monte_carlo_simulation(self, num_paths, num_steps):
    
        dt = self._maturity.maturity_in_years / num_steps
        nudt = (self._rate.get_rate() - 0.5 * self._volatility.get_volatility()**2) * dt
        volsdt = self._volatility.get_volatility() * np.sqrt(dt)
        paths = np.zeros((num_paths, num_steps + 1))
        paths[:, 0] = self._spot_price

        for step in range(1, num_steps + 1):
            random_shocks = np.random.normal(0, 1, num_paths)
            paths[:, step] = paths[:, step - 1] * np.exp(nudt + volsdt * random_shocks)
        return paths