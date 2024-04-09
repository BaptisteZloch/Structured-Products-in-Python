from abc import ABC, abstractmethod
from logging import warn
from typing import Dict, List, Optional, Union, Callable, Any
from scipy.optimize import minimize

from src.pricing.base.rate import Rate
from src.utility.types import Maturity


class ABCBond(ABC):
    """Abstract class that defines the main structure of a bond, the children will need to implement the constructor and the `compute_price` method."""

    def __init__(self) -> None:
        pass

    @abstractmethod
    def compute_price(self):
        pass


class Optimization:
    def __init__(
        self,
        pricing_function: Callable[[float], float],
        target_value: float,
        epsilon: float = 0.001,
        initial_value: float = 0.01,
    ) -> None:
        """Constructor of the optimization class that will be used to compute the YTM of a bond.

        Args:
        ----
            pricing_function (Callable[[float], float]): The pricing function used to compute the price for a given bond
            target_value (float): The desired value the optimizer needs to converge to.
            epsilon (float, optional): The tolerance. Defaults to 0.001.
            initial_value (float, optional): The initial guess for the optimization procedure. Defaults to 0.01.
        """
        self.__pricing_function = pricing_function
        self.__target_value = target_value
        self.__epsilon = epsilon
        self.__initial_value = initial_value

    def run(self):
        return minimize(
            lambda x: (self.__target_value - self.__pricing_function(x)) ** 2,
            x0=(self.__initial_value),
            method="SLSQP",
            tol=self.__epsilon,
        )


class ZeroCouponBond(ABCBond):
    _price: Optional[float] = None

    def __init__(
        self,
        rate: Rate,
        maturity: Maturity,
        nominal: int,
    ) -> None:
        """Constructor of the ZeroCouponBond class

        Args:
            rate (Rate): The Rate object that will be used to discount the price
            maturity (Maturity): The maturity object used to compute the pricing
            nominal (int): The nominal of the bond
        """
        self.__rate = rate
        self.__maturity = maturity
        self.__nominal = nominal

    def compute_price(self, force_rate: Optional[float] = None) -> float:
        """Compute the price of the bond.

        Args:
            force_rate (Optional[float], optional): Parameter used when optimizing for YTM, leave it to None else. Defaults to None.

        Returns:
            float: _description_
        """
        if self._price is None:
            self._price = self.__nominal * (
                self.__rate.discount_factor(
                    maturity=self.__maturity, force_rate=force_rate
                )
            )  # =~100 - TAUX x Maturité
        return self._price

class Bond(ABCBond):
    _price: Optional[float] = None
    _ytm: Optional[float] = None

    def __init__(
        self,
        rate: Rate,
        maturity: Maturity,
        nominal: int,
        coupon_rate: float,
        nb_coupon: int,
    ) -> None:
        self.__rate = rate
        self.__maturity = maturity
        self.__nominal = nominal
        self.__coupon_rate = coupon_rate
        self.__nb_coupon = nb_coupon
        self.__components = self.__run_components()

    def compute_price(self, force_rate: Optional[float] = None):
        if self._price is None or force_rate is not None:
            price = sum(
                [
                    zc_bond.get("zc_bond").compute_price(force_rate=force_rate)
                    for zc_bond in self.__components
                ]
            )

            if force_rate is not None:
                return price
            else:
                self._price = price
        return self._price

    def ytm(self):
        optimizer = Optimization(
            pricing_function=lambda rate: self.compute_price(force_rate=rate),
            target_value=self._price,
            initial_value=0.01,
        )
        optim_res = optimizer.run()
        if optim_res.status == 0:
            self._ytm = optim_res["x"][0]
        else:
            warn("Error while optimzing", optim_res)
        return self._ytm

    def __run_components(self):
        t = self.__maturity.maturity_in_years
        terms = []
        step = 1.0 / self.__nb_coupon
        while t > 0:
            terms.append(t)
            t -= step
        sorted(terms)
        freq_coupon = float(self.__coupon_rate) / self.__nb_coupon * self.__nominal
        coupons: List[Dict[str, Union[str, float, ZeroCouponBond]]] = [
            {
                "maturity": t,
                "cf_type": "coupon",
                "zc_bond": ZeroCouponBond(
                    self.__rate,
                    Maturity(maturity_in_years=t),
                    freq_coupon
                    + (
                        0.0 if t < self.__maturity.maturity_in_years else self.__nominal
                    ),  # type: ignore
                ),
            }
            for t in terms
        ]
        return coupons
