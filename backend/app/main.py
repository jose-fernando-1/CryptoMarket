
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.services.market_data import MarketDataService

from app.api.websocket import router as websocket_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    market = MarketDataService()

    app.state.market = market
    await market.start()

    try:
        yield
    finally:
        await market.stop()


app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time Bitcoin and Dollar monitoring API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "application": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }

app.include_router(router)
app.include_router(websocket_router)