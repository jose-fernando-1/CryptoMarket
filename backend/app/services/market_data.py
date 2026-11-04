
import asyncio
import logging
import httpx

from pydantic import ValidationError

from app.core.config import settings
from app.core.state import MarketState
from app.services.coinbase import CoinbaseService
from app.services.exchange_rate import ExchangeRateService


logger = logging.getLogger(__name__)


class MarketDataService:
    def __init__(self):
        self.state = MarketState()
        self.coinbase = CoinbaseService()
        self.exchange = ExchangeRateService()
        self.tasks: list[asyncio.Task] = []

    async def start(self):
        self.tasks = [
            asyncio.create_task(
                self._consume_bitcoin(),
                name="coinbase_stream",
            ),
            asyncio.create_task(
                self._poll_exchange_rate(),
                name="exchange_rate_poll",
            ),
        ]

    async def stop(self):
        for task in self.tasks:
            task.cancel()

        await asyncio.gather(
            *self.tasks,
            return_exceptions=True,
        )
        self.tasks.clear()

    async def _consume_bitcoin(self):
        async for price in self.coinbase.stream_prices():
            self.state.update_bitcoin(price)

    async def _poll_exchange_rate(self):
        while True:
            try:
                rate = await self.exchange.get_usd_brl()
                self.state.update_exchange_rate(rate)

            except (
                httpx.HTTPError,
                KeyError,
                ValueError,
                ValidationError,
            ) as exc:
                logger.warning(
                    "Erro ao atualizar USD/BRL: %s",
                    exc,
                )

            await asyncio.sleep(
                settings.EXCHANGE_UPDATE_INTERVAL
            )

    def get_snapshot(self) -> dict | None:
        return self.state.snapshot()
