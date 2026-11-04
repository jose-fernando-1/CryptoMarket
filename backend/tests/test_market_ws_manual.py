
import asyncio
import json

import websockets


async def main():
    uri = "ws://127.0.0.1:8000/ws/market"

    async with websockets.connect(uri) as websocket:
        print("Conectado ao CryptoMarket!")

        async for message in websocket:
            data = json.loads(message)

            print(
                f"BTC/USD: ${data['btc_usd']} | "
                f"BTC/BRL: R${data['btc_brl']} | "
                f"USD/BRL: R${data['usd_brl']['mid']}"
            )


if __name__ == "__main__":
    asyncio.run(main())
