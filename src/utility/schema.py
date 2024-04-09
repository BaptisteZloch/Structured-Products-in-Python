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
    spot_price: float = Field(
        default=100.0, description="Spot price of the underlying", gt=0
    )
    strike_price: float = Field(
        default=110.0, description="Strike price of the option", ge=0
    )
    maturity: float = Field(default=1, description="Maturity in years", gt=0)
    dividend: Optional[float] = Field(default=0.0, description="Dividend yield", ge=0)
    rate: Optional[float] = Field(
        default=None, description="Interest rates to calculate the price (discount)."
    )
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
        default=None,
        description="The implied volatility surface with first keys as maturity and second keys as moneyness.",
    )
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
    dividend: float = Field(default=0.0, description="Dividend yield", ge=0)
    rate: Optional[float] = Field(
        default=None, description="Interest rates to calculate the price (discount)."
    )
    rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Interest rates curve dictionary maturity as keys and rates as values",
    )
    volatility: Optional[float] = Field(
        default=None, description="The implied volatility"
    )
    volatility_surface: Optional[Dict[str, Dict[str, float]]] = Field(
        default=None,
        description="The implied volatility surface with first keys as maturity and second keys as moneyness.",
    )


class StraddleStrategyBaseModel(OptionStrategyBaseModel):
    strike_price: float = Field(..., description="Strike price of the straddle", gt=0)


class StrangleStrategyBaseModel(OptionStrategyBaseModel):
    strike_price1: float = Field(
        ..., description="First strike price of the strangle", gt=0
    )
    strike_price2: float = Field(
        ..., description="Second strike price of the strangle", gt=0
    )


class ButterflyStrategyBaseModel(OptionStrategyBaseModel):
    strike_price1: float = Field(
        ..., description="First strike price of the strangle", gt=0
    )
    strike_price2: float = Field(
        ..., description="Second strike price of the strangle", gt=0
    )

    strike_price3: float = Field(
        ..., description="Third strike price of the strangle", gt=0
    )


class CallSpreadStrategyBaseModel(OptionStrategyBaseModel):
    lower_strike: float = Field(..., description="lower price of the call spread", gt=0)
    upper_strike: float = Field(..., description="upper price of the call spread", gt=0)


class PutSpreadStrategyBaseModel(OptionStrategyBaseModel):
    lower_strike: float = Field(..., description="lower price of the put spread", gt=0)
    upper_strike: float = Field(..., description="upper price of the put spread", gt=0)


class StripStrategyBaseModel(OptionStrategyBaseModel):
    strike_price1: float = Field(
        ..., description="First strike price of the Strip", gt=0
    )
    strike_price2: float = Field(
        ..., description="Second strike price of the Strip", gt=0
    )


class StrapStrategyBaseModel(OptionStrategyBaseModel):
    strike_price1: float = Field(
        ..., description="First strike price of the Strap", gt=0
    )
    strike_price2: float = Field(
        ..., description="Second strike price of the Strap", gt=0
    )


class ZeroCouponBondBaseModel(BaseModel):
    rate: Optional[float] = Field(
        default=None, description="Interest rates to calculate the price (discount)."
    )
    rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Interest rates curve dictionary maturity as keys and rates as values",
    )
    maturity: float = Field(
        default=1, description="Maturity of the bond in years", gt=0
    )
    nominal: int = Field(
        default=1000, description="Nominal value of the bond in currency", gt=0
    )


class BondBaseModel(ZeroCouponBondBaseModel):
    coupon_rate: float = Field(
        default=0.05, description="Coupon rate of the bond", gt=0
    )
    nb_coupon: int = Field(default=1, description="Number of coupons in the bond", gt=0)


class StructuredProduct(BaseModel):
    spot_price: float = Field(
        default=100.0, description="Spot price of the underlying", gt=0
    )
    dividend: Optional[float] = Field(default=0.0, description="Dividend yield", ge=0)
    rate: Optional[float] = Field(default=None, description="Interest rates")
    rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Interest rates curve dictionary maturity as keys and rates as values",
    )
    volatility: Optional[float] = Field(
        default=None, description="The implied volatility"
    )
    volatility_surface: Optional[Dict[str, Dict[str, float]]] = Field(
        default=None,
        description="The implied volatility surface with first keys as maturity and second keys as moneyness.",
    )
    maturity: float = Field(default=1, description="Maturity in years", gt=0)
    strike_price: float = Field(
        default=100.0, description="Spot price of the underlying", gt=0
    )


class ReverseConvertibleBaseModel(StructuredProduct):
    nominal: int = Field(
        default=1000, description="Nominal value of the bond in currency", gt=0
    )

    converse_rate: float


class OutperformerCertificateBaseModel(StructuredProduct):
    foreign_rate: Optional[float] = Field(
        default=None, description="Foreign nterest rates"
    )
    foreign_rate_curve: Optional[Dict[str, float]] = Field(
        default=None,
        description="Foreign interest rates curve dictionary maturity as keys and rates as values",
    )
    participation: float = Field(
        default=1, description="The participation in (%), 1=100%.", ge=1
    )
