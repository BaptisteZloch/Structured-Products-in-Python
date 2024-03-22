import math
from typing import Dict, List, Literal, Optional
from scipy import interpolate

from src.utility.types import Maturity


class Rate:
    def __init__(
        self,
        rate: Optional[float] = None,
        rate_type: Literal["continuous", "compounded"] = "continuous",
        rate_curve: Optional[Dict[Maturity, float]] = None,
        interpolation_type: Literal["linear", "quadratic", "cubic"] = "linear",
    ) -> None:
        assert interpolation_type in [
            "linear",
            "quadratic",
            "cubic",
        ], 'Error provide either interpolation_type "linear", "quadratic", "cubic" '
        self.__rate = rate
        self.__rate_type = rate_type
        if rate_curve is not None:
            self.__interpol = interpolate.interp1d(
                [mat.maturity_in_years for mat in rate_curve.keys()],
                list(rate_curve.values()),
                fill_value="extrapolate",
                kind=interpolation_type,
            )

    def get_rate(self, maturity: Optional[Maturity] = None) -> float:
        if self.__rate is not None:
            return self.__rate
        if Maturity is not None:
            return float(self.__interpol(maturity.maturity_in_years))
        raise ValueError("Error, provide a valid maturity or a rate attribute.")

    def discount_factor(
        self, maturity: Maturity, force_rate: Optional[float] = None
    ) -> float:
        """Compute the discount factor given a maturity.

        Args:
            maturity (Maturity): Object maturity output the maturity in years.

        Raises:
            ValueError: _description_

        Returns:
            float: The discount factor
        """

        if self.__rate_type == "continuous":
            return math.exp(
                -(
                    self.get_rate(maturity=maturity)
                    if force_rate is None
                    else force_rate
                )
                * maturity.maturity_in_years
            )
        elif self.__rate_type == "compounded":
            return 1.0 / (
                (
                    1
                    + (
                        self.get_rate(maturity=maturity)
                        if force_rate is None
                        else force_rate
                    )
                )
                ** maturity.maturity_in_years
            )
        else:
            raise ValueError("Error provide a valid rate type")
