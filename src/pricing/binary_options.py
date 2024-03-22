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

    def compute_delta(self):
        d2 = self._d2
        if self._option_type == "call":
            delta = np.exp(-self._rate.get_rate() * self._maturity.maturity_in_years) * norm.pdf(d2) / (self._spot_price * self._volatility.get_volatility() * np.sqrt(self._maturity.maturity_in_years))
        elif self._option_type == "put":
            delta = -np.exp(-self._rate.get_rate() * self._maturity.maturity_in_years) * norm.pdf(-d2) / (self._spot_price * self._volatility.get_volatility() * np.sqrt(self._maturity.maturity_in_years))
        else:
            raise ValueError("Option type not supported. Use 'call' or 'put'.")
        return delta
    
    def compute_gamma(self):
    
        d1 = self._d1
        d2 = self._d2
        tau = self._maturity.maturity_in_years
        S = self._spot_price
        sigma = self._volatility.get_volatility()
        r = self._rate.get_rate()

        if self._option_type == "call":
            gamma = -np.exp(-r * tau) * norm.pdf(d2) * d1 / (S**2 * sigma**2 * tau)
        elif self._option_type == "put":
            gamma = np.exp(-r * tau) * norm.pdf(d2) * d1 / (S**2 * sigma**2 * tau)
        else:
            raise ValueError("Option type not supported. Use 'call' or 'put'.")

        return gamma



    def compute_vega(self):
        d1 = self._d1
        d2 = self._d2
        if self._option_type == "call":
            vega = np.exp(-self._rate.get_rate() * self._maturity.maturity_in_years) * d1 * norm.pdf(d2) / self._volatility.get_volatility()
        elif self._option_type == "put":
            vega = -np.exp(-self._rate.get_rate() * self._maturity.maturity_in_years) * d1 * norm.pdf(d2) / self._volatility.get_volatility()
        else:
            raise ValueError("Option type not supported. Use 'call' or 'put'.")
        return vega

    def compute_rho(self):
        d2 = self._d2
        if self._option_type == "call":
            rho = np.exp(-self._rate.get_rate() * self._maturity.maturity_in_years) * (np.sqrt(self._maturity.maturity_in_years) * norm.pdf(d2) / self._volatility.get_volatility() - self._maturity.maturity_in_years * norm.cdf(d2)) / 100
        elif self._option_type == "put":
            rho = np.exp(-self._rate.get_rate() * self._maturity.maturity_in_years) * (-np.sqrt(self._maturity.maturity_in_years) * norm.pdf(-d2) / self._volatility.get_volatility() - self._maturity.maturity_in_years * norm.cdf(-d2)) / 100
        else:
            raise ValueError("Option type not supported. Use 'call' or 'put'.")
        return rho

    def compute_theta(self):
        d2 = self._d2
        tau = self._maturity.maturity_in_years
        S = self._spot_price
        K = self._strike_price
        sigma = self._volatility.get_volatility()
        r = self._rate.get_rate()
        
        common_factor = np.exp(-r * tau) * norm.pdf(d2) / (2 * tau * sigma * np.sqrt(tau))
        ln_part = np.log(S / K) - (r - (sigma**2 / 2) * tau)
        
        if self._option_type == "call":
            theta = common_factor * (ln_part + r * norm.cdf(d2))
        elif self._option_type == "put":
            theta = common_factor * (ln_part - r * norm.cdf(-d2))
        else:
            raise ValueError("Option type not supported. Use 'call' or 'put'.")
        theta = theta / 365
        
        return theta


    def compute_greeks(self):
        return {
            "delta": self.compute_delta(),
            "gamma": self.compute_gamma(),
            "theta": self.compute_theta(),
            "rho": self.compute_rho(),
            "vega": self.compute_vega(),
        }