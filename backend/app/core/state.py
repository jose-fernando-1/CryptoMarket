
from decimal import Decimal

from app.schemas.market import BitcoinPrice, ExchangeRate


class MarketState:
    def __init__(self):
        self.bitcoin: BitcoinPrice | None = None
        self.exchange_rate: ExchangeRate | None = None

    def update_bitcoin(self, price: BitcoinPrice) -> None:
        self.bitcoin = price

    def update_exchange_rate(self, rate: ExchangeRate) -> None:
        self.exchange_rate = rate

    def snapshot(self) -> dict | None:
        if self.bitcoin is None or self.exchange_rate is None:
            return None

        btc_usd = self.bitcoin.price
        rate = self.exchange_rate

        # Cotação média indicativa entre compra e venda
        usd_brl_mid = (rate.bid + rate.ask) / Decimal("2")

        return {
            "pair": "BTC/USD",
            "btc_usd": str(btc_usd),
            "btc_brl": str(btc_usd * usd_brl_mid),
            "usd_brl": {
                "bid": str(rate.bid),
                "ask": str(rate.ask),
                "mid": str(usd_brl_mid),
            },
            "btc_timestamp": self.bitcoin.timestamp.isoformat(),
            "fx_timestamp": rate.timestamp.isoformat(),
            "sources": {
                "bitcoin": self.bitcoin.source,
                "exchange": rate.source,
            },
        }
