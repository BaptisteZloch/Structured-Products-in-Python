from typing import Any, Dict
from pydantic import BaseModel

from src.pricing.structured_products import OutperformerCertificate, ReverseConvertible
from src.pricing.barrier_options import BarrierOption
from src.pricing.base.rate import Rate
from src.pricing.base.volatility import Volatility
from src.pricing.binary_options import BinaryOption
from src.pricing.fixed_income import Bond, ZeroCouponBond
from src.pricing.option_strategies import (
    ButterflyStrategy,
    StraddleStrategy,
    StrangleStrategy,
    CallSpreadStrategy,
    PutSpreadStrategy,
    StripStrategy,
    StrapStrategy,
)
from src.pricing.vanilla_options import VanillaOption
from src.utility.schema import (
    BarrierOptionBaseModel,
    BinaryOptionBaseModel,
    ButterflyStrategyBaseModel,
    CallSpreadStrategyBaseModel,
    OptionBaseModel,
    OutperformerCertificateBaseModel,
    PutSpreadStrategyBaseModel,
    ReverseConvertibleBaseModel,
    StraddleStrategyBaseModel,
    StrangleStrategyBaseModel,
    StrapStrategyBaseModel,
    StripStrategyBaseModel,
    ZeroCouponBondBaseModel,
)
from src.utility.types import Maturity


class PricingService:
    @staticmethod
    def __handle_rate_and_rate_curve_base_model(base_model_dict: Dict[str, Any]):
        if "rate" in base_model_dict.keys():
            base_model_dict["rate"] = Rate(rate=base_model_dict["rate"])
        elif "rate_curve" in base_model_dict.keys():
            base_model_dict["rate_curve"] = Rate(
                rate_curve={
                    Maturity(float(maturity_string)): rates
                    for maturity_string, rates in base_model_dict["rate_curve"].items()
                }
            )
            base_model_dict["rate"] = base_model_dict.pop("rate_curve")
        else:
            raise ValueError("Error, provide either rate or rate_curve argument")
        return base_model_dict

    @staticmethod
    def __handle_vol_and_vol_surface_base_model(base_model_dict: Dict[str, Any]):
        if "volatility" in base_model_dict.keys():
            base_model_dict["volatility"] = Volatility(
                volatility=base_model_dict["volatility"]
            )
        elif "volatility_surface" in base_model_dict.keys():
            raise NotImplementedError()
            # base_model_dict["rate_curve"] = Rate(
            #     rate_curve={
            #         Maturity(float(maturity_string)): rates
            #         for maturity_string, rates in base_model_dict["rate_curve"].items()
            #     }
            # )
            # base_model_dict["rate"] = base_model_dict.pop("rate_curve")
        else:
            raise ValueError(
                "Error, provide either volatility or volatility_surface argument"
            )
        return base_model_dict

    @staticmethod
    def process_outperformer_certificate_structured_product(
        request_received_model: OutperformerCertificateBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        opt = OutperformerCertificate(**product_dict)
        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_reverse_convertible_structured_product(
        request_received_model: ReverseConvertibleBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        opt = ReverseConvertible(**product_dict)
        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_binary_options(
        request_received_model: BinaryOptionBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])

        product_dict = PricingService.__handle_vol_and_vol_surface_base_model(
            product_dict
        )
        opt = BinaryOption(
            spot_price=product_dict["spot_price"],
            strike_price=product_dict["strike_price"],
            maturity=product_dict["maturity"],
            rate=product_dict["rate"],
            volatility=product_dict["volatility"],
            option_type=product_dict["option_type"],
            dividend=product_dict["dividend"],
        )
        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_vanilla_options(
        request_received_model: OptionBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)

        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )

        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict = PricingService.__handle_vol_and_vol_surface_base_model(
            product_dict
        )
        opt = VanillaOption(
            spot_price=product_dict["spot_price"],
            strike_price=product_dict["strike_price"],
            maturity=product_dict["maturity"],
            rate=product_dict["rate"],
            volatility=product_dict["volatility"],
            option_type=product_dict["option_type"],
            dividend=product_dict["dividend"],
        )

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_barrier_options(
        request_received_model: BarrierOptionBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)

        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict = PricingService.__handle_vol_and_vol_surface_base_model(
            product_dict
        )
        opt = BarrierOption(**product_dict)

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_vanilla_bond(request_received_model: BaseModel) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        opt = Bond(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_zero_coupon_bond(
        request_received_model: ZeroCouponBondBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        opt = ZeroCouponBond(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_straddle_strategy(
        request_received_model: StraddleStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict = PricingService.__handle_vol_and_vol_surface_base_model(
            product_dict
        )
        opt = StraddleStrategy(
            spot_price=product_dict["spot_price"],
            strike_price=product_dict["strike_price"],
            maturity=product_dict["maturity"],
            rate=product_dict["rate"],
            volatility=product_dict["volatility"],
            dividend=product_dict["dividend"],
        )

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_strangle_strategy(
        request_received_model: StrangleStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict = PricingService.__handle_vol_and_vol_surface_base_model(
            product_dict
        )
        opt = StrangleStrategy(
            spot_price=product_dict["spot_price"],
            strike_price1=product_dict["strike_price1"],
            strike_price2=product_dict["strike_price2"],
            maturity=product_dict["maturity"],
            rate=product_dict["rate"],
            volatility=product_dict["volatility"],
            dividend=product_dict["dividend"],
        )

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_butterfly_strategy(
        request_received_model: ButterflyStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict = PricingService.__handle_vol_and_vol_surface_base_model(
            product_dict
        )
        opt = ButterflyStrategy(
            spot_price=product_dict["spot_price"],
            strike_price1=product_dict["strike_price1"],
            strike_price2=product_dict["strike_price2"],
            strike_price3=product_dict["strike_price3"],
            maturity=product_dict["maturity"],
            rate=product_dict["rate"],
            volatility=product_dict["volatility"],
            dividend=product_dict["dividend"],
        )

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_call_spread_strategy(
        request_received_model: CallSpreadStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict = PricingService.__handle_vol_and_vol_surface_base_model(
            product_dict
        )
        opt = CallSpreadStrategy(
            spot_price=product_dict["spot_price"],
            lower_strike=product_dict["lower_strike"],
            upper_strike=product_dict["upper_strike"],
            maturity=product_dict["maturity"],
            rate=product_dict["rate"],
            volatility=product_dict["volatility"],
            dividend=product_dict["dividend"],
        )

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_put_spread_strategy(
        request_received_model: PutSpreadStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict = PricingService.__handle_vol_and_vol_surface_base_model(
            product_dict
        )
        opt = PutSpreadStrategy(
            spot_price=product_dict["spot_price"],
            lower_strike=product_dict["lower_strike"],
            upper_strike=product_dict["upper_strike"],
            maturity=product_dict["maturity"],
            rate=product_dict["rate"],
            volatility=product_dict["volatility"],
            dividend=product_dict["dividend"],
        )

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_strip_strategy(
        request_received_model: StripStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict = PricingService.__handle_vol_and_vol_surface_base_model(
            product_dict
        )
        opt = StripStrategy(
            spot_price=product_dict["spot_price"],
            strike_price1=product_dict["strike_price1"],
            strike_price2=product_dict["strike_price2"],
            maturity=product_dict["maturity"],
            rate=product_dict["rate"],
            volatility=product_dict["volatility"],
            dividend=product_dict["dividend"],
        )

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_strap_strategy(
        request_received_model: StrapStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict = PricingService.__handle_rate_and_rate_curve_base_model(
            product_dict
        )
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict = PricingService.__handle_vol_and_vol_surface_base_model(
            product_dict
        )
        opt = StrapStrategy(
            spot_price=product_dict["spot_price"],
            strike_price1=product_dict["strike_price1"],
            strike_price2=product_dict["strike_price2"],
            maturity=product_dict["maturity"],
            rate=product_dict["rate"],
            volatility=product_dict["volatility"],
            dividend=product_dict["dividend"],
        )

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())
