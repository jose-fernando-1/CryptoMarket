from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Bitcoin Monitor"
    APP_ENV: str = "development"

    COINBASE_WS_URL: str = (
        "wss://advanced-trade-ws.coinbase.com"
    )

    COINBASE_REST_URL: str = (
        "https://api.coinbase.com/api/v3/brokerage"
    )

    EXCHANGE_API_URL: str = (
        "https://economia.awesomeapi.com.br"
    )

    EXCHANGE_UPDATE_INTERVAL: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
