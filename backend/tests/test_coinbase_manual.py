
import asyncio

from app.services.coinbase import CoinbaseService


async def main():
    service = CoinbaseService()

    async for price in service.stream_prices():
        print(price.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
