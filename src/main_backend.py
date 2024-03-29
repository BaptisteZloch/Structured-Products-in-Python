import os
import sys
from typing import Dict, Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from src.services.pricing_service import PricingService
from src.utility.schema import (
    BarrierOptionBaseModel,
    BinaryOptionBaseModel,
    BondBaseModel,
    ButterflyStrategyBaseModel,
    CallSpreadStrategyBaseModel,
    OptionBaseModel,
    OutperformerCertificateBaseModel,
    PricingResultBaseModel,
    PutSpreadStrategyBaseModel,
    ReverseConvertibleBaseModel,
    StraddleStrategyBaseModel,
    StrangleStrategyBaseModel,
    StrapStrategyBaseModel,
    StripStrategyBaseModel,
    ZeroCouponBondBaseModel,
)
from src.utility.types import (
    BondType,
    OptionKindType,
    OptionStrategyType,
    ProductKindType,
)

app = FastAPI()

# AVAILABLE at:  https://structured-pricing-api-dauphine.koyeb.app/docs
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


@app.post(
    "/api/v1/price/structured-product/{product_kind}",
    response_model=PricingResultBaseModel,
)
def structured_product_pricing(
    product_kind: ProductKindType,
    product: Union[ReverseConvertibleBaseModel, OutperformerCertificateBaseModel],
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    try:
        if product_kind == "reverse-convertible" and isinstance(
            product, ReverseConvertibleBaseModel
        ):
            return pricing_service.process_reverse_convertible_structured_product(
                product
            )
        if product_kind == "outperformer-certificate" and isinstance(
            product, OutperformerCertificateBaseModel
        ):
            return pricing_service.process_outperformer_certificate_structured_product(
                product
            )
        raise ValueError("Provide valid input.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option/{option_kind}", response_model=PricingResultBaseModel)
def option_pricing(
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
    {
        "spot_price":100,
        "strike_price": 100,
        "maturity": 1,
        "rate_curve": {"0.5":0.02,"1":0.06},
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        raise HTTPException(
            status_code=404,
            detail=f"{e} | {exc_type} | {os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]} | {exc_tb.tb_lineno}",
        ) from e


@app.post(
    "/api/v1/price/option-strategy/{option_strategy}",
    response_model=PricingResultBaseModel,
    description="Function that prices the options strategies : straddle, strangle, butterfly, call-spread, put-spread, strip, strap. ",
)
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        raise HTTPException(
            status_code=404,
            detail=f"{e} | {exc_type} | {os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]} | {exc_tb.tb_lineno}",
        ) from e


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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        raise HTTPException(
            status_code=404,
            detail=f"{e} | {exc_type} | {os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]} | {exc_tb.tb_lineno}",
        ) from e


@app.get("/")
def base_url():
    try:
        return RedirectResponse("/docs")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        raise HTTPException(
            status_code=404,
            detail=f"{e} | {exc_type} | {os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]} | {exc_tb.tb_lineno}",
        ) from e


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
