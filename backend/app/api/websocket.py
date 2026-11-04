
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws/market")
async def market_websocket(websocket: WebSocket):
    await websocket.accept()

    market = websocket.app.state.market
    last_snapshot = None

    try:
        while True:
            snapshot = market.get_snapshot()

            if snapshot is not None and snapshot != last_snapshot:
                await websocket.send_json(snapshot)
                last_snapshot = snapshot

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    except asyncio.CancelledError:
        raise
    except OSError:
        pass
    finally:
        print("Cliente WebSocket desconectado")
