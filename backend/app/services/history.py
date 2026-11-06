
import asyncio
from bisect import bisect_right
from datetime import datetime, timedelta, timezone

from app.schemas.market import BitcoinBRLHistory
from app.services.coinbase import CoinbaseService
from app.services.exchange_rate import ExchangeRateService


class MarketHistoryService:
    def __init__(self):
        self.coinbase = CoinbaseService()
        self.exchange = ExchangeRateService()

    async def get_btc_brl_history(
        self,
        limit: int = 60,
    ) -> list[BitcoinBRLHistory]:

        end = datetime.now(timezone.utc)
        start = end - timedelta(minutes=limit)

        btc_history, fx_history = await asyncio.gather(
            self.coinbase.get_candles(
                start=start,
                end=end,
                granularity="ONE_MINUTE",
            ),
            self.exchange.get_usd_brl_history(limit=100),
        )


        # -----------------------------------------
        # Ordenação do histórico de câmbio
        # -----------------------------------------

        fx_history.sort(key=lambda rate: rate.timestamp)

        fx_times = [
            rate.timestamp for rate in fx_history
        ]

        result = []

        # Contadores para diagnóstico
        skipped_no_fx = 0
        skipped_stale_fx = 0

        # -----------------------------------------
        # Sincronização BTC/USD + USD/BRL
        # -----------------------------------------

        for candle in btc_history:

            # Última cotação FX disponível
            # até o início do candle.
            index = bisect_right(
                fx_times,
                candle.timestamp,
            ) - 1

            if index < 0:
                skipped_no_fx += 1
                continue

            rate = fx_history[index]

            age = candle.timestamp - rate.timestamp

            # Descartar câmbio com mais de 5 minutos.
            if age > timedelta(minutes=5):
                skipped_stale_fx += 1
                continue

            result.append(
                BitcoinBRLHistory(
                    timestamp=candle.timestamp,
                    btc_usd=candle.close,
                    usd_brl=rate.mid,
                    btc_brl=candle.close * rate.mid,
                    fx_timestamp=rate.timestamp,
                )
            )

        return result
