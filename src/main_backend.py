import os
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException, Depends

import uvicorn

from pricing.base.rate import Rate
from pricing.base.volatility import Volatility
from pricing.binary_options import BinaryOption
from services.pricing_service import PricingService
from utility.schema import BinaryOptionBaseModel, OptionBaseModel
from utility.types import Maturity

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
):
    try:
        return pricing_service.process_binary_options(product)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}") from e


@app.post("/api/v1/price/option/vanilla")
def vanilla_option_pricing(
    product: OptionBaseModel,
    pricing_service: PricingService = Depends(PricingService),
):
    try:
        return pricing_service.process_vanilla_options(product)
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
