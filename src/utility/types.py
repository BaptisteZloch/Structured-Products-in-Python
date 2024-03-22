from datetime import datetime
from typing import Dict, Optional, Literal


DayCountConvention = Literal["ACT/360", "ACT/365"]


OptionType = Literal["call", "put"]
BarrierType = Literal["KO", "KI"]
OptionKindType = Literal["vanilla", "binary", "barrier"]
BondType = Literal["vanilla", "zero-coupon"]
OptionStrategyType = Literal[
    "straddle", "strangle", "butterfly", "call-spread", "put-spread", "strip", "strap"
]


class Maturity:
    DAY_COUNT_MAPPING: Dict[DayCountConvention, float] = {
        "ACT/360": 360.0,
        "ACT/365": 365.0,
    }

    def __init__(
        self,
        maturity_in_years: Optional[float] = None,
        maturity_in_days: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        day_count_convention: DayCountConvention = "ACT/360",
    ):
        """Compute the maturity in year given a maturity in days, years, between dates... and a day count convention.

        Args:
            maturity_in_years (Optional[float], optional): _description_. Defaults to None.
            maturity_in_days (Optional[float], optional): _description_. Defaults to None.
            start_date (Optional[datetime], optional): _description_. Defaults to None.
            end_date (Optional[datetime], optional): _description_. Defaults to None.
            day_count_convention (Literal[&quot;ACT, optional): _description_. Defaults to "ACT/360".
        """
        if maturity_in_years is not None:
            self.__maturity_in_years = maturity_in_years
        elif maturity_in_days is not None:
            self.__maturity_in_years = maturity_in_days / self.DAY_COUNT_MAPPING.get(
                day_count_convention, 365.0
            )
        elif start_date is not None and end_date is not None:
            self.__maturity_in_years = (
                end_date - start_date
            ).days / self.DAY_COUNT_MAPPING.get(day_count_convention, 365.0)
        else:
            raise ValueError(
                "Error, provide valid inputs either start_date/end_date, maturity_in_days or maturity_in_years"
            )

    @property
    def maturity_in_years(self) -> float:
        return self.__maturity_in_years
