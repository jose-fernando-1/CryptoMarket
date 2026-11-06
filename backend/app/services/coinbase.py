
import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from decimal import Decimal

import httpx
import websockets

from app.core.config import settings
from app.schemas.market import BitcoinPrice, Candle

logger = logging.getLogger(__name__)


class CoinbaseService:
    def __init__(self):
        self.ws_url = settings.COINBASE_WS_URL
        self.product_id = "BTC-USD"

    async def stream_prices(self) -> AsyncIterator[BitcoinPrice]:
        retry_delay = 1

        while True:
            try:
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=20,
                    open_timeout=10,
                ) as websocket:
                    logger.info("Conectado à Coinbase")

                    for channel in ("ticker", "heartbeats"):
                        await websocket.send(json.dumps({
                            "type": "subscribe",
                            "product_ids": [self.product_id],
                            "channel": channel,
                        }))

                    retry_delay = 1

                    async for message in websocket:
                        data = json.loads(message)

                        if data.get("channel") != "ticker":
                            continue

                        for event in data.get("events", []):
                            for ticker in event.get("tickers", []):
                                if ticker.get("product_id") != self.product_id:
                                    continue

                                yield BitcoinPrice(
                                    pair="BTC/USD",
                                    price=Decimal(ticker["price"]),
                                    timestamp=datetime.fromisoformat(
                                        data["timestamp"].replace("Z", "+00:00")
                                    ),
                                    source="coinbase",
                                )

            except (
                websockets.exceptions.ConnectionClosed,
                OSError,
                TimeoutError,
            ) as exc:
                logger.warning(
                    "Conexão Coinbase interrompida: %s",
                    exc
                )

            logger.info(
                "Reconectando em %s segundos",
                retry_delay
            )
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 30)


    async def get_candles(
        self,
        start: datetime,
        end: datetime,
        granularity: str = "ONE_MINUTE",
    ) -> list[Candle]:

        url = (
            f"{settings.COINBASE_REST_URL}"
            f"/market/products/BTC-USD/candles"
        )

        params = {
            "start": str(int(start.timestamp())),
            "end": str(int(end.timestamp())),
            "granularity": granularity,
            "limit": 300,
        }

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        candles = [
            Candle(
                timestamp=datetime.fromtimestamp(
                    int(item["start"]),
                    tz=timezone.utc,
                ),
                open=Decimal(item["open"]),
                high=Decimal(item["high"]),
                low=Decimal(item["low"]),
                close=Decimal(item["close"]),
                volume=Decimal(item["volume"]),
            )
            for item in data["candles"]
        ]

        return sorted(candles, key=lambda c: c.timestamp)
