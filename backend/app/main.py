from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time Bitcoin and Dollar monitoring API",
    version="0.1.0"
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "application": settings.APP_NAME,
        "environment": settings.APP_ENV
    }
