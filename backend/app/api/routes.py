
import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.market import ExchangeRate
from app.services.exchange_rate import ExchangeRateService


router = APIRouter(prefix="/api/v1", tags=["Market"])

exchange_service = ExchangeRateService()


@router.get("/exchange-rate", response_model=ExchangeRate)
async def get_exchange_rate():
    try:
        return await exchange_service.get_usd_brl()
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Serviço de câmbio indisponível"
        ) from exc
