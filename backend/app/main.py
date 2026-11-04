from fastapi import FastAPI

from app.core.config import settings

from app.api.routes import router
app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time Bitcoin and Dollar monitoring API",
    version="0.1.0"
)

app.include_router(router)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "application": settings.APP_NAME,
        "environment": settings.APP_ENV
    }
