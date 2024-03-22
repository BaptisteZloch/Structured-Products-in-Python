from typing import Dict
from pydantic import BaseModel

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
    PutSpreadStrategyBaseModel,
    StraddleStrategyBaseModel,
    StrangleStrategyBaseModel,
    StrapStrategyBaseModel,
    StripStrategyBaseModel,
    ZeroCouponBondBaseModel,
)
from src.utility.types import Maturity


class PricingService:
    @staticmethod
    def process_binary_options(
        request_received_model: BinaryOptionBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = BinaryOption(**product_dict)
        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_vanilla_options(
        request_received_model: OptionBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = VanillaOption(**product_dict)

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_barrier_options(
        request_received_model: BarrierOptionBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = BarrierOption(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_vanilla_bond(request_received_model: BaseModel) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        opt = Bond(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_zero_coupon_bond(
        request_received_model: ZeroCouponBondBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        opt = ZeroCouponBond(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_straddle_strategy(
        request_received_model: StraddleStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = StraddleStrategy(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_strangle_strategy(
        request_received_model: StrangleStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = StrangleStrategy(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_butterfly_strategy(
        request_received_model: ButterflyStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = ButterflyStrategy(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_call_spread_strategy(
        request_received_model: CallSpreadStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = CallSpreadStrategy(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_put_spread_strategy(
        request_received_model: PutSpreadStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = PutSpreadStrategy(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_strip_strategy(
        request_received_model: StripStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = StripStrategy(**product_dict)

        return {"price": opt.compute_price()}

    @staticmethod
    def process_strap_strategy(
        request_received_model: StrapStrategyBaseModel,
    ) -> Dict[str, float]:
        product_dict = request_received_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = StrapStrategy(**product_dict)

        return {"price": opt.compute_price()}