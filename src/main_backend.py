import os
import sys
from typing import Annotated, Dict, Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body, FastAPI, HTTPException, Depends
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

app = FastAPI(
    title="StructurerAPI",
    description=" This app is a structurer aimed app. The goal is to provide an programming interface (API) flexible that could be used to price different type of products quickly.<br><br>You will be able to:<br><ul><li>Price Bonds</li><li>Price Options</li><li>Price Options strategies</li><li>Price Structured products</li></ul>",
    summary="API for structured products and derivatives pricing.",
    version="0.0.1",
    contact={
        "name": "Naim LEHBIBEN - Hugo SOLEAU - Matthieu MONNOT - Baptiste ZLOCH",
        "email": "baptiste.zloch@dauphine.eu",
    },
    license_info={
        "name": "Apache 4.0",
        "url": "https://www.apache.org/licenses/LICENSE-4.0.html",
    },
)

# AVAILABLE at:  https://structured-pricing-api-dauphine.koyeb.app/docs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "https://structured-pricing-api-dauphine.koyeb.app",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.post(
    "/api/v1/price/structured-product/{product_kind}",
    response_model=PricingResultBaseModel,
)
def structured_product_pricing(
    product_kind: ProductKindType,
    product: Annotated[
        Union[ReverseConvertibleBaseModel, OutperformerCertificateBaseModel],
        Body(
            openapi_examples={
                "reverse_convertible": {
                    "summary": "Reverse convertible",
                    "description": "Reverse convertible example without neither vol surface nor rate curve",
                    "value": {
                        "spot_price": 100,
                        "maturity": 1,
                        "rate": 0.03,
                        "coupon": 0.05,
                        "dividend": 0.0,
                        "volatility": 0.20,
                    },
                },
                "reverse_convertible_vol_surf": {
                    "summary": "Reverse convertible with volatility surface",
                    "description": "Reverse convertible example without rate curve",
                    "value": {
                        "spot_price": 100,
                        "maturity": 1,
                        "rate": 0.03,
                        "coupon": 0.05,
                        "dividend": 0.0,
                        "volatility_surface": {
                            "1.0": {"0.9": 0.14, "1.0": 0.10, "1.1": 0.12},
                            "1.5": {"0.9": 0.13, "1.0": 0.09, "1.1": 0.13},
                            "2.0": {"0.9": 0.10, "1.0": 0.1, "1.1": 0.08},
                        },
                    },
                },
                "reverse_convertible_vol_surf_rate_curve": {
                    "summary": "Reverse convertible with volatility surface and rate curve",
                    "description": "Reverse convertible example",
                    "value": {
                        "spot_price": 100,
                        "maturity": 1,
                        "rate_curve": {"0.5": 0.02, "1": 0.06},
                        "coupon": 0.05,
                        "dividend": 0.0,
                        "volatility_surface": {
                            "1.0": {"0.9": 0.14, "1.0": 0.10, "1.1": 0.12},
                            "1.5": {"0.9": 0.13, "1.0": 0.09, "1.1": 0.13},
                            "2.0": {"0.9": 0.10, "1.0": 0.1, "1.1": 0.08},
                        },
                    },
                },
                "outperformer": {
                    "summary": "Outperformer Certificate",
                    "description": "Outperformer Certificate example without neither vol surface nor rate curve. Note that the volatility surface or the rate curve could be specified in the same manner than the reverse convertible.",
                    "value": {
                        "spot_price": 100,
                        "maturity": 1,
                        "rate": 0.03,
                        "dividend": 0.0,
                        "volatility": 0.20,
                        "participation": 1.2,
                        "foreign_rate": 0.02,
                    },
                },
            },
        ),
    ],
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    """This API `HTTP POST` method can be used to price structured products.The 2 structured products that could be priced are outperformer certificate and reverse convertible.
    The parameters that has to be in the JSON body are specified in the example section below.
    The structured product to price needs to be specified in the URL.

    Args:
    ----
        product_kind (ProductKindType): The type of structured product to price among 'reverse-convertible', 'outperformer-certificate'.
        product (Union[OutperformerCertificateBaseModel,ReverseConvertibleBaseModel]): The schema corresponding to the JSON body sent by the user. The details are available in the section below (example).
        pricing_service (PricingService, optional): PricingService is a static class providing services to converge JSON schema to actual class while processing the input and returning the price and the associated greek. Defaults to Depends(PricingService).

    Raises:
    ----
        ValueError: Whether the user provides wrong arguments to the function.
        HTTPException: The details of any other error occurring during the pricing.

    Returns:
    ----
        Dict[str, float]: A dict representing with keys as price and greek names and values as computed values.
    """
    try:
        if product_kind == "reverse-convertible":
            return pricing_service.process_reverse_convertible_structured_product(
                ReverseConvertibleBaseModel(**product.model_dump(exclude_unset=True))
            )
        if product_kind == "outperformer-certificate":
            return pricing_service.process_outperformer_certificate_structured_product(
                OutperformerCertificateBaseModel(
                    **product.model_dump(exclude_unset=True)
                )
            )
        raise ValueError("Provide valid input.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option/{option_kind}", response_model=PricingResultBaseModel)
def option_pricing(
    option_kind: OptionKindType,
    product: Annotated[
        Union[BarrierOptionBaseModel, BinaryOptionBaseModel, OptionBaseModel],
        Body(
            openapi_examples={
                "vanilla_binary_options": {
                    "summary": "Vanilla or Binary option",
                    "description": "Normal example without neither vol surface nor rate curve",
                    "value": {
                        "spot_price": 100,
                        "strike_price": 100,
                        "maturity": 1,
                        "rate": 0.05,
                        "dividend": 0.0,
                        "volatility": 0.2,
                        "option_type": "call",
                    },
                },
                "vanilla_binary_options_rates": {
                    "summary": "Vanilla or Binary option with Rate curve",
                    "description": "Normal example without vol surface",
                    "value": {
                        "spot_price": 100,
                        "strike_price": 100,
                        "maturity": 1,
                        "dividend": 0.0,
                        "rate_curve": {"0.5": 0.02, "1": 0.06},
                        "volatility": 0.2,
                        "option_type": "call",
                    },
                },
                "vanilla_binary_options_volsurface": {
                    "summary": "Vanilla or Binary option with volatility surface",
                    "description": "Normal example without rate curve",
                    "value": {
                        "spot_price": 100,
                        "strike_price": 110,
                        "maturity": 1,
                        "rate": 0.03,
                        "dividend": 0.0,
                        "volatility_surface": {
                            "1.0": {"0.9": 0.14, "1.0": 0.10, "1.1": 0.12},
                            "1.5": {"0.9": 0.13, "1.0": 0.09, "1.1": 0.13},
                            "2.0": {"0.9": 0.10, "1.0": 0.1, "1.1": 0.08},
                        },
                        "option_type": "call",
                    },
                },
                "barrier_option": {
                    "summary": "Barrier options",
                    "description": "Normal example without neither rate curve or volatility surface however it can be used the same way.",
                    "value": {
                        "spot_price": 80,
                        "strike_price": 100,
                        "maturity": 0.5,
                        "rate": 0.03,
                        "dividend": 0.0,
                        "volatility": 0.20,
                        "option_type": "put",
                        "barrier_level": 80,
                        "barrier_type": "ki",
                        "barrier_direction": "down",
                    },
                },
            },
        ),
    ],
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    """This API `HTTP POST` method can be used to price options.The 3 options that could be priced are vanilla, barrier and binary options.
    The parameters that has to be in the JSON body are specified in the example section below.
    The options to price needs to be specified in the URL.

    Args:
    ----
        option_kind (OptionKindType): The type of option to price among 'vanilla', 'binary', 'barrier'.
        product (Union[BinaryOptionBaseModel, OptionBaseModel, BarrierOptionBaseModel]): The schema corresponding to the JSON body sent by the user. The details are available in the section below (example)
        pricing_service (PricingService, optional): PricingService is a static class providing services to converge JSON schema to actual class while processing the input and returning the price and the associated greek. Defaults to Depends(PricingService).

    Raises:
    ----
        ValueError: Whether the user provides wrong arguments to the function.
        HTTPException: The details of any other error occurring during the pricing.

    Returns:
    ----
        Dict[str, float]: A dict representing with keys as price and greek names and values as computed values.
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
        exc_type, _, exc_tb = sys.exc_info()
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
    product: Annotated[
        Union[
            ButterflyStrategyBaseModel,
            StraddleStrategyBaseModel,
            StripStrategyBaseModel,
            StrapStrategyBaseModel,
            StrangleStrategyBaseModel,
            CallSpreadStrategyBaseModel,
            PutSpreadStrategyBaseModel,
        ],
        Body(
            openapi_examples={
                "straddle": {
                    "summary": "Straddle",
                    "description": "Straddle example without neither vol surface nor rate curve",
                    "value": {
                        "spot_price": 100,
                        "strike_price": 100,
                        "maturity": 1,
                        "rate": 0.05,
                        "dividend": 0.0,
                        "volatility": 0.2,
                    },
                },
                "straddle_rc": {
                    "summary": "Straddle with rate curve",
                    "description": "Straddle example without vol surface",
                    "value": {
                        "spot_price": 100,
                        "strike_price": 100,
                        "maturity": 1,
                        "rate_curve": {"0.5": 0.02, "1": 0.06},
                        "dividend": 0.0,
                        "volatility": 0.2,
                    },
                },
                "straddle_rc_vs": {
                    "summary": "Straddle with rate curve and volatility surface",
                    "description": "Straddle full example",
                    "value": {
                        "spot_price": 100,
                        "strike_price": 100,
                        "maturity": 1,
                        "rate_curve": {"0.5": 0.02, "1": 0.06},
                        "dividend": 0.0,
                        "volatility_surface": {
                            "1.0": {"0.9": 0.14, "1.0": 0.10, "1.1": 0.12},
                            "1.5": {"0.9": 0.13, "1.0": 0.09, "1.1": 0.13},
                            "2.0": {"0.9": 0.10, "1.0": 0.1, "1.1": 0.08},
                        },
                    },
                },
                "strangle": {
                    "summary": "Strangle",
                    "description": "Strangle example without neither vol surface nor rate curve. Constrains : strike_price1 < strike_price2 ",
                    "value": {
                        "spot_price": 100,
                        "strike_price1": 100,
                        "strike_price2": 110,
                        "maturity": 1,
                        "rate": 0.05,
                        "dividend": 0,
                        "volatility": 0.2,
                    },
                },
                "call_spread": {
                    "summary": "Call Spread",
                    "description": "Call Spread example without neither vol surface nor rate curve. Constrains : lower_strike < upper_strike ",
                    "value": {
                        "spot_price": 100,
                        "upper_strike": 110,
                        "lower_strike": 100,
                        "maturity": 1,
                        "rate": 0.05,
                        "dividend": 0,
                        "volatility": 0.2,
                    },
                },
                "put_spread": {
                    "summary": "Put Spread",
                    "description": "Put Spread example without neither vol surface nor rate curve. Constrains : lower_strike < upper_strike ",
                    "value": {
                        "spot_price": 100,
                        "upper_strike": 110,
                        "lower_strike": 100,
                        "maturity": 1,
                        "rate": 0.05,
                        "dividend": 0,
                        "volatility": 0.2,
                    },
                },
                "strip": {
                    "summary": "Strip",
                    "description": "Strip example without neither vol surface nor rate curve. Constrains : strike_price1 < strike_price2 ",
                    "value": {
                        "spot_price": 100,
                        "strike_price1": 90,
                        "strike_price2": 100,
                        "maturity": 1,
                        "rate": 0.05,
                        "dividend": 0,
                        "volatility": 0.2,
                    },
                },
                "strap": {
                    "summary": "Strap",
                    "description": "Strap example without neither vol surface nor rate curve. Constrains : strike_price1 < strike_price2 ",
                    "value": {
                        "spot_price": 100,
                        "strike_price1": 90,
                        "strike_price2": 100,
                        "maturity": 1,
                        "rate": 0.05,
                        "dividend": 0,
                        "volatility": 0.2,
                    },
                },
                "butterfly": {
                    "summary": "Butterfly",
                    "description": "Butterfly example without neither vol surface nor rate curve. Constrains : strike_price1 < strike_price2 ",
                    "value": {
                        "spot_price": 100,
                        "strike_price1": 90,
                        "strike_price2": 100,
                        "strike_price3": 110,
                        "maturity": 1,
                        "rate": 0.05,
                        "dividend": 0,
                        "volatility": 0.2,
                    },
                },
            },
        ),
    ],
    pricing_service: PricingService = Depends(PricingService),
) -> Dict[str, float]:
    """This API `HTTP POST` method can be used to price option strategies.The 7 option strategies that could be priced are: `straddle, strangle, butterfly, call-spread, put-spread, strip, strap`.
    The parameters that has to be in the JSON body are specified in the example section below.
    The options strategies to price needs to be specified in the URL.

    Args:
    ----
        option_kind (OptionKindType): The type of option strategy to price among 'straddle', 'strangle', 'butterfly', 'call-spread', 'put-spread', 'strip', 'strap'.
        product (Union[ ButterflyStrategyBaseModel, StraddleStrategyBaseModel, StripStrategyBaseModel, StrapStrategyBaseModel, StrangleStrategyBaseModel, CallSpreadStrategyBaseModel, PutSpreadStrategyBaseModel, ]): The schema corresponding to the JSON body sent by the user. The details are available in the section below (example)
        pricing_service (PricingService, optional): PricingService is a static class providing services to converge JSON schema to actual class while processing the input and returning the price and the associated greek. Defaults to Depends(PricingService).

    Raises:
    ----
        ValueError: Whether the user provides wrong arguments to the function.
        HTTPException: The details of any other error occurring during the pricing.

    Returns:
    ----
        Dict[str, float]: A dict representing with keys as price and greek names and values as computed values.
    """
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
        if option_strategy == "straddle":
            return pricing_service.process_straddle_strategy(
                StraddleStrategyBaseModel(**product.model_dump(exclude_unset=True))
            )
        if option_strategy == "strangle":
            return pricing_service.process_strangle_strategy(
                StrangleStrategyBaseModel(**product.model_dump(exclude_unset=True))
            )
        if option_strategy == "butterfly":
            return pricing_service.process_butterfly_strategy(
                ButterflyStrategyBaseModel(**product.model_dump(exclude_unset=True))
            )
        if option_strategy == "call-spread":
            return pricing_service.process_call_spread_strategy(
                CallSpreadStrategyBaseModel(**product.model_dump(exclude_unset=True))
            )
        if option_strategy == "put-spread":
            return pricing_service.process_put_spread_strategy(
                PutSpreadStrategyBaseModel(**product.model_dump(exclude_unset=True))
            )
        if option_strategy == "strip":
            return pricing_service.process_strip_strategy(
                StripStrategyBaseModel(**product.model_dump(exclude_unset=True))
            )
        if option_strategy == "strap":
            return pricing_service.process_strap_strategy(
                StrapStrategyBaseModel(**product.model_dump(exclude_unset=True))
            )
        raise ValueError("Provide valid input.")
    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        raise HTTPException(
            status_code=404,
            detail=f"{e} | {exc_type} | {os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]} | {exc_tb.tb_lineno}",
        ) from e


@app.post("/api/v1/price/bond/{bond_type}")
def bond_pricing(
    bond_type: BondType,
    product: Annotated[
        Union[BondBaseModel, ZeroCouponBondBaseModel],
        Body(
            openapi_examples={
                "zero_coupon": {
                    "summary": "Zero coupon",
                    "description": "Zero coupon example",
                    "value": {"rate": 0.05, "maturity": 1, "nominal": 1000},
                },
                "zero_coupon_rate_curve": {
                    "summary": "Zero coupon with rate curve",
                    "description": "Zero coupon example with rate curve argument instead of rate.",
                    "value": {
                        "rate_curve": {"0.5": 0.02, "1": 0.06},
                        "maturity": 1,
                        "nominal": 1000,
                    },
                },
                "bond": {
                    "summary": "Vanilla Bond",
                    "description": "Vanilla Bond example, you can use rate curve argument instead of rate as with ZC bonds.",
                    "value": {
                        "rate": 0.05,
                        "maturity": 1,
                        "nominal": 1000,
                        "coupon_rate": 0.2,
                        "nb_coupon": 2,
                    },
                },
            },
        ),
    ],
    pricing_service: PricingService = Depends(PricingService),
):
    """This API `HTTP POST` method can be used to price bonds.The 2 bonds that could be priced are: `vanilla, zero-coupon`.
    The parameters that has to be in the JSON body are specified in the example section below.
    The options strategies to price needs to be specified in the URL.


    Args:
    ----
        product (BondBaseModel): The schema corresponding to the JSON body sent by the user. The details are available in the section below (example)
        pricing_service (PricingService, optional): PricingService is a static class providing services to converge JSON schema to actual class while processing the input and returning the price and the associated greek. Defaults to Depends(PricingService).

    Raises:
    ----
        ValueError: Whether the user provides wrong arguments to the function.
        HTTPException: The details of any other error occurring during the pricing.

    Returns:
    ----
        Dict[str, float]: A dict representing with keys as price and greek names and values as computed values.
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
    """Base URL that redirect to `/docs`.

    Raises:
    ----
        HTTPException: The details of any other error occurring during the pricing.

    """
    try:
        return RedirectResponse("/docs")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        raise HTTPException(
            status_code=404,
            detail=f"{e} | {exc_type} | {os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]} | {exc_tb.tb_lineno}",
        ) from e
