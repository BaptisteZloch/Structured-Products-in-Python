from pydantic import BaseModel, Field

from utility.types import BarrierType, OptionType


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


class BarrierOptionBaseModel(OptionBaseModel):
    spot_price: float = Field(..., description="Spot price of the underlying")
    strike_price: float
    maturity: float
    rate: float
    volatility: float
    option_type: OptionType
    barrier_level: float
    barrier_type: BarrierType


class OptionStrategyBaseModel(BaseModel):
    spot_price: float
    maturity: float
    rate: float
    volatility: float


class StraddleStrategyBaseModel(OptionStrategyBaseModel):
    strike_price: float


class StrangleStrategyBaseModel(OptionStrategyBaseModel):
    strike_price1: float
    strike_price2: float


class ButterflyStrategyBaseModel(OptionStrategyBaseModel):
    strike_price1: float
    strike_price2: float
    strike_price3: float


class CallSpreadStrategyBaseModel(OptionStrategyBaseModel):
    lower_strike: float
    upper_strike: float


class PutSpreadStrategyBaseModel(OptionStrategyBaseModel):
    lower_strike: float
    upper_strike: float


class StripStrategyBaseModel(OptionStrategyBaseModel):
    strike_price1: float
    strike_price2: float


class StrapStrategyBaseModel(OptionStrategyBaseModel):
    strike_price1: float
    strike_price2: float


class ZeroCouponBondBaseModel(BaseModel):
    rate: float
    maturity: float
    nominal: int


class BondBaseModel(ZeroCouponBondBaseModel):
    coupon_rate: float
    nb_coupon: int
