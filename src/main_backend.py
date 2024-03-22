from typing import Dict, Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends
from src.services.pricing_service import PricingService
from src.utility.schema import (
    BarrierOptionBaseModel,
    BinaryOptionBaseModel,
    BondBaseModel,
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
from src.utility.types import BondType, OptionKindType, OptionStrategyType

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/price/option/{option_kind}")
def binary_option_pricing(
    option_kind: OptionKindType,
    product: Union[BinaryOptionBaseModel, OptionBaseModel, BarrierOptionBaseModel],
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    """Send json like:
    ```json
    {
        "spot_price":100,
        "strike_price": 100,
        "maturity": 1,
        "rate": 0.05,
        "volatility": 0.2,
        "option_type": "call"
    }
    ```

    Args:
        option_kind (OptionKindType): _description_
        product (Union[BinaryOptionBaseModel, OptionBaseModel, BarrierOptionBaseModel]): _description_
        pricing_service (PricingService, optional): _description_. Defaults to Depends(PricingService).

    Raises:
        ValueError: _description_
        HTTPException: _description_

    Returns:
        Dict[str, float]: _description_
    """
    try:
        if option_kind == "binary" and isinstance(product, BinaryOptionBaseModel):
            return pricing_service.process_binary_options(product)
        if option_kind == "vanilla" and isinstance(product, OptionBaseModel):
            return pricing_service.process_vanilla_options(product)
        if option_kind == "barrier" and isinstance(product, BarrierOptionBaseModel):
            return pricing_service.process_barrier_options(product)
        raise ValueError("Provide valid input.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


# https://structured-pricing-api-dauphine.koyeb.app/docs


@app.post("/api/v1/price/option-strategy/{option_strategy}")
def option_strategy_pricing(
    option_strategy: OptionStrategyType,
    product: Union[
        StraddleStrategyBaseModel,
        StrangleStrategyBaseModel,
        ButterflyStrategyBaseModel,
        CallSpreadStrategyBaseModel,
        PutSpreadStrategyBaseModel,
        StripStrategyBaseModel,
        StrapStrategyBaseModel,
    ],
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    try:
        assert option_strategy in [
            "straddle",
            "strangle",
            "butterfly",
            "call-spread",
            "put-spread",
            "strip",
            "strap",
        ], "Error provide a valid strategy among: straddle, strangle, butterfly, call-spread, put-spread, strip, strap"
        if option_strategy == "straddle" and isinstance(
            product, StraddleStrategyBaseModel
        ):
            return pricing_service.process_straddle_strategy(product)
        if option_strategy == "strangle" and isinstance(
            product, StrangleStrategyBaseModel
        ):
            return pricing_service.process_strangle_strategy(product)
        if option_strategy == "butterfly" and isinstance(
            product, ButterflyStrategyBaseModel
        ):
            return pricing_service.process_butterfly_strategy(product)

        if option_strategy == "call-spread" and isinstance(
            product, CallSpreadStrategyBaseModel
        ):
            return pricing_service.process_call_spread_strategy(product)
        if option_strategy == "put-spread" and isinstance(
            product, PutSpreadStrategyBaseModel
        ):
            return pricing_service.process_put_spread_strategy(product)
        if option_strategy == "strip" and isinstance(product, StripStrategyBaseModel):
            return pricing_service.process_strip_strategy(product)
        if option_strategy == "strap" and isinstance(product, StrapStrategyBaseModel):
            return pricing_service.process_strap_strategy(product)
        raise ValueError("Provide valid input.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/bond/{bond_type}")
def bond_pricing(
    bond_type: BondType,
    product: Union[BondBaseModel, ZeroCouponBondBaseModel],
    pricing_service: PricingService = Depends(PricingService),
):
    """Send json like:
    ```json
    {
        "rate":0.05,
        "maturity":1,
        "nominal":1000,
        "coupon_rate":0.2,
        "nb_coupon":2
    }
    ``` or
    ```json
    {
        "rate":0.05,
        "maturity":1,
        "nominal":1000
    }
    ```

    Args:
        product (BondBaseModel): _description_
        pricing_service (PricingService, optional): _description_. Defaults to Depends(PricingService).

    Raises:
        HTTPException: Catching all exception

    Returns:
        Dict[str, float]: _description_
    """

    try:
        assert bond_type in [
            "vanilla",
            "zero-coupon",
        ], "Error provide a valid bond type among: vanilla, zero-coupon"
        if bond_type == "vanilla" and isinstance(product, BondBaseModel):
            return pricing_service.process_vanilla_bond(product)
        if bond_type == "zero-coupon" and isinstance(product, ZeroCouponBondBaseModel):
            return pricing_service.process_zero_coupon_bond(product)
        raise ValueError("Provide valid input.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.get("/")
def base_url():
    try:
        return {
            "message": "success ! The available routes are : `/api/v1/price/option/vanilla` and `/api/v1/price/option/binary`"
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


# def start():
#     if os.getenv("APP_ENV", "dev") == "dev":
#         uvicorn.run(
#             "main_backend:app",
#             host="0.0.0.0",
#             port=int(os.getenv("APP_PORT", "8000")),
#             # workers=4,
#             reload=True,
#         )
#     else:
#         uvicorn.run(
#             "main_backend:app",
#             host="0.0.0.0",
#             port=int(os.getenv("APP_PORT", "8000")),
#             reload=False,
#             workers=4,
#         )


# if __name__ == "__main__":
#     start()
