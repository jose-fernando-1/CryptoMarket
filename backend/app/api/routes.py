
import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.market import ExchangeRate
from app.services.exchange_rate import ExchangeRateService

from datetime import datetime, timedelta, timezone
from typing import Literal

from app.schemas.market import Candle
from app.services.coinbase import CoinbaseService

from fastapi import Request

from fastapi import Query
from app.schemas.market import ExchangeRateHistory

from app.schemas.market import BitcoinBRLHistory
from app.services.history import MarketHistoryService

router = APIRouter(prefix="/api/v1", tags=["Market"])

exchange_service = ExchangeRateService()
history_service = MarketHistoryService()


@router.get("/exchange-rate", response_model=ExchangeRate)
async def get_exchange_rate():
    try:
        return await exchange_service.get_usd_brl()
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Serviço de câmbio indisponível"
        ) from exc


@router.get("/market")
async def get_market(request: Request):
    market = request.app.state.market
    snapshot = market.get_snapshot()

    if snapshot is None:
        raise HTTPException(
            status_code=503,
            detail="Aguardando cotações de mercado",
        )

    return snapshot

Granularity = Literal[
    "ONE_MINUTE",
    "FIVE_MINUTE",
    "FIFTEEN_MINUTE",
    "ONE_HOUR",
    "ONE_DAY",
]

SECONDS = {
    "ONE_MINUTE": 60,
    "FIVE_MINUTE": 300,
    "FIFTEEN_MINUTE": 900,
    "ONE_HOUR": 3600,
    "ONE_DAY": 86400,
}


@router.get("/history/btc", response_model=list[Candle])
async def get_bitcoin_history(
    granularity: Granularity = "ONE_MINUTE",
    limit: int = 60,
):
    if not 1 <= limit <= 300:
        raise HTTPException(
            status_code=422,
            detail="limit deve estar entre 1 e 300",
        )

    end = datetime.now(timezone.utc)
    start = end - timedelta(
        seconds=SECONDS[granularity] * limit
    )

    try:
        service = CoinbaseService()
        return await service.get_candles(
            start=start,
            end=end,
            granularity=granularity,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Histórico Coinbase indisponível",
        ) from exc

@router.get(
    "/history/usd-brl",
    response_model=list[ExchangeRateHistory],
)
async def get_usd_brl_history(
    limit: int = Query(default=60, ge=1, le=100),
):
    try:
        return await exchange_service.get_usd_brl_history(
            limit=limit
        )
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Histórico USD/BRL indisponível",
        ) from exc

@router.get(
    "/history/btc-brl",
    response_model=list[BitcoinBRLHistory],
)
async def get_btc_brl_history(
    limit: int = Query(default=60, ge=1, le=300),
):
    try:
        return await history_service.get_btc_brl_history(
            limit=limit
        )
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Histórico BTC/BRL indisponível",
        ) from exc
