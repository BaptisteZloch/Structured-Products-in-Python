from typing import Dict, Optional


class Volatility:
    def __init__(
        self,
        volatility: Optional[float] = None,
        volatility_surface: Optional[Dict] = None,
    ) -> None:
        self.__volatility = volatility

    def get_volatility(
        self, strike_price: Optional[float] = None, maturity: Optional[float] = None
    ) -> float:
        if self.__volatility is not None:
            return self.__volatility
        else:
            raise NotImplementedError()
