from typing import Dict, Optional
from pydantic import BaseModel, Field

from src.utility.types import BarrierType, OptionType


class PricingResultBaseModel(BaseModel):
    price: float
    delta: float
    gamma: float
    theta: float
    rho: float
    vega: float


class OptionBaseModel(BaseModel):
    spot_price: float = Field(..., description="Spot price of the underlying")
    strike_price: float = Field(..., description="Spot price of the underlying")
    maturity: float = Field(..., description="Maturity in years")
    dividend: Optional[float] = Field(default=0.0, description="Dividend yield")
    rate: Optional[float] = Field(default=None, description="Interest rates")
    rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Interest rates curve dictionary maturity as keys and rates as values",
    )
    volatility: float
    # volatility: Optional[float] = Field(default=None, description="The implied volatility")
    # volatility_surface: Optional[float] = Field(default=None, description="The implied volatility")
    option_type: OptionType


class BinaryOptionBaseModel(OptionBaseModel):
    pass


class BarrierOptionBaseModel(OptionBaseModel):
    option_type: OptionType
    barrier_level: float
    barrier_type: BarrierType


class OptionStrategyBaseModel(BaseModel):
    spot_price: float
    maturity: float
    dividend: float = Field(default=0.0, description="Dividend yield")
    rate: Optional[float] = Field(default=None, description="Interest rates")
    rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Interest rates curve dictionary maturity as keys and rates as values",
    )
    volatility: float
    # volatility: Optional[float] = Field(default=None, description="The implied volatility")
    # volatility_surface: Optional[float] = Field(default=None, description="The implied volatility")


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
    rate: Optional[float] = Field(default=None, description="Interest rates")
    rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Interest rates curve dictionary maturity as keys and rates as values",
    )
    maturity: float
    nominal: int


class BondBaseModel(ZeroCouponBondBaseModel):
    coupon_rate: float
    nb_coupon: int


class ReverseConvertibleBaseModel(BaseModel):
    pass


class OutperformerCertificateBaseModel(BaseModel):
    pass
