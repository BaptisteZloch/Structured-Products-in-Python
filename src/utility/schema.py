from typing import Optional
from pydantic import BaseModel, Field

from utility.types import OptionType


class OptionBaseModel(BaseModel):
    spot_price: float = Field(..., description="Spot price of the underlying")
    strike_price: float
    maturity: float
    rate: float
    volatility: float
    option_type: OptionType


class BinaryOptionBaseModel(OptionBaseModel):
    spot_price: float = Field(..., description="Spot price of the underlying")
    strike_price: float
    maturity: float
    rate: float
    volatility: float
    option_type: OptionType


class ZeroCouponBondBaseModel(BaseModel):
    rate: float
    maturity: float
    nominal: int


class BondBaseModel(ZeroCouponBondBaseModel):
    coupon_rate: float
    nb_coupon: int
