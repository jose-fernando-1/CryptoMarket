
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ExchangeRate(BaseModel):
    pair: str
    bid: Decimal
    ask: Decimal
    timestamp: datetime
    source: str


class BitcoinPrice(BaseModel):
    pair: str
    price: Decimal
    timestamp: datetime
    source: str
