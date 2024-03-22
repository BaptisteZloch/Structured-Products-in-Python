from typing import Dict, Optional
import matplotlib.pyplot as plt
from scipy.interpolate import RectBivariateSpline
import numpy as np


class Volatility:
    def __init__(
        self,
        volatility: Optional[float] = None,
        volatility_surface: Optional[Dict] = None,
        interpol_type: str = "quintic",
    ) -> None:
        self.__volatility = volatility
        self.__volatility_surface = volatility_surface
        self.__interpol_type = interpol_type

        if volatility_surface is not None:
            if interpol_type not in ["linear", "cubic", "quintic"]:
                raise ValueError("Invalid interpolation type")

            stpr = sorted(set([k[0] for k in volatility_surface.keys()]))
            mat = sorted(set([k[1] for k in volatility_surface.keys()]))

            if len(stpr) < 2 or len(mat) < 2:
                raise Exception(
                    "Not enough data points to interpolate on the volatility surface."
                )

            Stpr, Mat = np.meshgrid(stpr, mat)

            VS = np.array(
                [
                    [volatility_surface[(K, T)] for K, T in zip(row_K, row_T)]
                    for row_K, row_T in zip(Stpr, Mat)
                ]
            )
            self.__interpol = RectBivariateSpline(stpr, mat, VS.T, kx=2, ky=2)

    def get_volatility(
        self, strike_price: Optional[float] = None, maturity: Optional[float] = None
    ) -> float:
        if self.__volatility is not None:
            return self.__volatility
        elif self.__interpol is not None:
            if strike_price is None or maturity is None:
                raise ValueError(
                    "Both strike_price and maturity must be provided for interpolation."
                )

            try:
                volatility = self.__interpol(strike_price, maturity)
                return float(volatility)
            except ValueError:
                raise ValueError(
                    "Interpolation failed for the provided strike_price and maturity."
                )
        else:
            raise ValueError(
                "Volatility surface interpolation has not been initialized."
            )

    def print_surface(
        self, n_points: Optional[int] = None, colour: Optional[str] = None
    ) -> None:
        if self.__interpol is not None:
            stpr, mat = self.__interpol.get_knots()

            if n_points is None:
                n_points = 100

            strike_prices = np.linspace(min(stpr), max(stpr), n_points)
            maturities = np.linspace(min(mat), max(mat), n_points)
            K, T = np.meshgrid(strike_prices, maturities)

            S = self.__interpol(strike_prices, maturities)

            if colour is None:
                colour = "viridis"

            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")
            ax.plot_surface(K, T, S, cmap=colour)
            ax.set_xlabel("Strike Price")
            ax.set_ylabel("Maturity")
            ax.set_zlabel("Volatility")
            ax.set_title("Volatility Surface")
            plt.show()
        else:
            raise ValueError("Interpolation function must be provided.")

    def __str__(self) -> str:
        """
        Provides a human-readable string representation of the OptionBase object.

        Returns:
            str: A string representation of the option including spot price, strike price,
                maturity, option type, and volatility.
        """
        if self.__volatility is not None:
            return f"Volatility<volatility={self.__volatility:.2f}>"


if __name__ == "__main__":
    volatility_surface_example = {
        (1.0, 0.5): 0.2,
        (1.5, 0.5): 0.3,
        (2.0, 0.5): 0.1,
        (1.0, 0.75): 0.22,
        (1.5, 0.75): 0.32,
        (2.0, 0.75): 0.12,
        (1.0, 1.0): 0.21,
        (1.5, 1.0): 0.29,
        (2.0, 1.0): 0.1,
    }

    volatility_object = Volatility(volatility_surface=volatility_surface_example)

    volatility_object.print_surface()

    print(volatility_object.get_volatility(1.3, 0.75))
