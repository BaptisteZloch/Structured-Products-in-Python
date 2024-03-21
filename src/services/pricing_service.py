from typing import Dict
from pydantic import BaseModel

from pricing.base.rate import Rate
from pricing.base.volatility import Volatility
from pricing.binary_options import BinaryOption
from pricing.vanilla_options import VanillaOption
from utility.types import Maturity


class PricingService:
    @staticmethod
    def process_binary_options(pydantic_model: BaseModel) -> Dict[str, float]:
        product_dict = pydantic_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = BinaryOption(**product_dict)
        return dict({"price": opt.compute_price()}, **opt.compute_greeks())

    @staticmethod
    def process_vanilla_options(pydantic_model: BaseModel) -> Dict[str, float]:
        product_dict = pydantic_model.model_dump(exclude_unset=True)
        product_dict["rate"] = Rate(rate=product_dict["rate"])
        product_dict["maturity"] = Maturity(maturity_in_years=product_dict["maturity"])
        product_dict["volatility"] = Volatility(volatility=product_dict["volatility"])
        opt = VanillaOption(**product_dict)

        return dict({"price": opt.compute_price()}, **opt.compute_greeks())
