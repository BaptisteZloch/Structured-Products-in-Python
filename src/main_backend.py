import os
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException, Depends

import uvicorn

from services.pricing_service import PricingService
from utility.schema import (
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


@app.post("/api/v1/price/option/binary")
def binary_option_pricing(
    product: BinaryOptionBaseModel,
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
        product (BinaryOptionBaseModel): _description_
        pricing_service (PricingService, optional): _description_. Defaults to Depends(PricingService).

    Raises:
        HTTPException: Catching all exception

    Returns:
        Dict[str, float]: _description_
    """
    try:
        return pricing_service.process_binary_options(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option/vanilla")
def vanilla_option_pricing(
    product: OptionBaseModel,
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    """Send json like :
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
        product (OptionBaseModel): _description_
        pricing_service (PricingService, optional): _description_. Defaults to Depends(PricingService).

    Raises:
        HTTPException: Catching all exception

    Returns:
        Dict[str, float]: _description_
    """
    try:
        return pricing_service.process_vanilla_options(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option-strategy/straddle")
def straddle_strategy_pricing(
    product: StraddleStrategyBaseModel,
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    try:
        return pricing_service.process_straddle_strategy(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option-strategy/strangle")
def strangle_strategy_pricing(
    product: StrangleStrategyBaseModel,
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    try:
        return pricing_service.process_strangle_strategy(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option-strategy/butterfly")
def butterfly_strategy_pricing(
    product: ButterflyStrategyBaseModel,
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    try:
        return pricing_service.process_butterfly_strategy(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option-strategy/call-spread")
def call_spread_strategy_pricing(
    product: CallSpreadStrategyBaseModel,
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    try:
        return pricing_service.process_call_spread_strategy(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option-strategy/put-spread")
def put_spread_strategy_pricing(
    product: PutSpreadStrategyBaseModel,
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    try:
        return pricing_service.process_put_spread_strategy(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option-strategy/strip")
def strip_strategy_pricing(
    product: StripStrategyBaseModel,
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    try:
        return pricing_service.process_strip_strategy(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option-strategy/strap")
def strap_strategy_pricing(
    product: StrapStrategyBaseModel,
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    try:
        return pricing_service.process_strap_strategy(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/bond/vanilla")
def vanilla_bond_pricing(
    product: BondBaseModel,
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
        return pricing_service.process_vanilla_bond(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/bond/zerocoupon")
def zero_coupon_bond_pricing(
    product: ZeroCouponBondBaseModel,
    pricing_service: PricingService = Depends(PricingService),
):
    """Send json like :
    ```json
    {
        "rate":0.05,
        "maturity":1,
        "nominal":1000
    }
    ```

    Args:
        product (ZeroCouponBondBaseModel): _description_
        pricing_service (PricingService, optional): _description_. Defaults to Depends(PricingService).

    Raises:
        HTTPException: Catching all exception

    Returns:
        Dict[str, float]: _description_
    """
    try:
        return pricing_service.process_zero_coupon_bond(product)
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


def start():
    if os.getenv("APP_ENV", "dev") == "dev":
        uvicorn.run(
            "main_backend:app",
            host="0.0.0.0",
            port=int(os.getenv("APP_PORT", "8000")),
            # workers=4,
            reload=True,
        )
    else:
        uvicorn.run(
            "main_backend:app",
            host="0.0.0.0",
            port=int(os.getenv("APP_PORT", "8000")),
            reload=False,
            workers=4,
        )


if __name__ == "__main__":
    start()
