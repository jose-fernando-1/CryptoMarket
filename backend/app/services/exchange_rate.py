
from datetime import datetime, timezone
from decimal import Decimal

import httpx

from app.core.config import settings
from app.schemas.market import ExchangeRate


class ExchangeRateService:
    def __init__(self):
        self.base_url = settings.EXCHANGE_API_URL

    async def get_usd_brl(self) -> ExchangeRate:
        url = f"{self.base_url}/json/last/USD-BRL"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            data = response.json()["USDBRL"]

        return ExchangeRate(
            pair="USD/BRL",
            bid=Decimal(data["bid"]),
            ask=Decimal(data["ask"]),
            timestamp=datetime.fromtimestamp(
                int(data["timestamp"]),
                tz=timezone.utc
            ),
            source="awesomeapi"
        )
