from typing import Dict, Optional
from pydantic import BaseModel, Field

from src.utility.types import BarrierDirection, BarrierType, OptionType


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
    foreign_rate: Optional[float] = Field(
        default=None, description="Foreign interest rate for FX options"
    )
    rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Interest rates curve dictionary maturity as keys and rates as values",
    )
    volatility: Optional[float] = Field(
        default=None, description="The implied volatility"
    )
    volatility_surface: Optional[Dict[str, Dict[str, float]]] = Field(
        default=None, description="The implied volatility"
    )
    # Maturity en première clé et Strike en seconde
    # {
    #     '0.3':{'0.9':0.14,'1':0.14,'1.1':0.14,},
    #     '0.5':{'0.9':0.14,1:0.14,'1.1':0.14,},
    #     1:{'0.9':0.14,'1':0.14,'1.1':0.14,},
    # }
    option_type: OptionType


class BinaryOptionBaseModel(OptionBaseModel):
    pass


class BarrierOptionBaseModel(OptionBaseModel):
    barrier_level: float = Field(..., description="Barrier level for the option")
    barrier_type: BarrierType = Field(..., description="Barrier type:  ko/ki")
    barrier_direction: BarrierDirection = Field(..., description="Barrier type up/down")


class OptionStrategyBaseModel(BaseModel):
    spot_price: float = Field(
        default=100.0, description="Spot price of the underlying", gt=0
    )
    maturity: float = Field(default=1.0, description="Maturity in years", gt=0)
    dividend: float = Field(default=0.0, description="Dividend yield")
    rate: Optional[float] = Field(default=None, description="Interest rates")
    rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Interest rates curve dictionary maturity as keys and rates as values",
    )
    volatility: Optional[float] = Field(
        default=None, description="The implied volatility"
    )
    volatility_surface: Optional[Dict[str, Dict[str, float]]] = Field(
        default=None, description="The implied volatility"
    )
    # Maturity en première clé et Strike en seconde
    # {
    #     '0.3':{'0.9':0.14,'1':0.14,'1.1':0.14,},
    #     '0.5':{'0.9':0.14,1:0.14,'1.1':0.14,},
    #     1:{'0.9':0.14,'1':0.14,'1.1':0.14,},
    # }
    # volatility_surface: Optional[float] = Field(default=None, description="The implied volatility")


class StraddleStrategyBaseModel(OptionStrategyBaseModel):
    strike_price: float = Field(..., description="Strike price of the straddle")


class StrangleStrategyBaseModel(OptionStrategyBaseModel):
    strike_price1: float = Field(..., description="First strike price of the strangle")
    strike_price2: float = Field(..., description="Second strike price of the strangle")


class ButterflyStrategyBaseModel(OptionStrategyBaseModel):
    strike_price1: float
    strike_price2: float
    strike_price3: float


class CallSpreadStrategyBaseModel(OptionStrategyBaseModel):
    lower_strike: float
    upper_strike: float


class PutSpreadStrategyBaseModel(CallSpreadStrategyBaseModel):
    pass


class StripStrategyBaseModel(StrangleStrategyBaseModel):
    pass


class StrapStrategyBaseModel(StripStrategyBaseModel):
    pass


class ZeroCouponBondBaseModel(BaseModel):
    rate: Optional[float] = Field(default=None, description="Interest rates")
    rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Interest rates curve dictionary maturity as keys and rates as values",
    )
    maturity: float = Field(default=1, description="Maturity of the bond", gt=0)
    nominal: int = Field(default=1000, description="Nominal value of the bond", gt=0)


class BondBaseModel(ZeroCouponBondBaseModel):
    coupon_rate: float = Field(
        default=0.05, description="Coupon rate of the bond", gt=0
    )
    nb_coupon: int = Field(default=1, description="Number of coupons in the bond", gt=0)


class StructuredProduct(BaseModel):
    spot_price: float = Field(..., description="Spot price of the underlying")
    dividend: Optional[float] = Field(default=0.0, description="Dividend yield")
    rate: Optional[float] = Field(default=None, description="Interest rates")
    rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Interest rates curve dictionary maturity as keys and rates as values",
    )
    volatility: Optional[float] = Field(
        default=None, description="The implied volatility"
    )
    volatility_surface: Optional[Dict[str, Dict[str, float]]] = Field(
        default=None, description="The implied volatility"
    )
    maturity: float = Field(..., description="Maturity in years")
    strike_price: float = Field(..., description="Spot price of the underlying")


class ReverseConvertibleBaseModel(StructuredProduct):
    nominal: int
    converse_rate: float


class OutperformerCertificateBaseModel(StructuredProduct):
    foreign_rate: Optional[float] = Field(
        default=None, description="Foreign nterest rates"
    )
    foreign_rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Foreign interest rates curve dictionary maturity as keys and rates as values",
    )
    participation: float
