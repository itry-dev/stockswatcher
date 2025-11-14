from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "stockswatcher"
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    TELEGRAM_NOTIFICATION_ENABLED: bool = False
    CHECK_INTERVAL_MINUTES: int = 5
    NEAR_LEVEL_PCT: float = 0.005 # 0,5%
    TICKER_MAP: Dict[str, str] = {
        "TXN": "TXN",
        "INTC": "INTC",
        "STM": "STMMI.MI",
        "ENI": "ENI.MI",
        "ENEL": "ENEL.MI",
    }


settings = Settings()