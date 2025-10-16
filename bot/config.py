import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
    PARSER_BASE_URL: str = os.getenv("PARSER_BASE_URL", "")
    ENV: str = os.getenv("ENV", "dev")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "storage/database.db")
    FUN_MIN_INTERVAL: int = int(os.getenv("FUN_MIN_INTERVAL", "1800"))
    FUN_MAX_INTERVAL: int = int(os.getenv("FUN_MAX_INTERVAL", "5400"))
    FAN_COOLDOWN_SECONDS: int = int(os.getenv("FAN_COOLDOWN_SECONDS", "1200"))
    FUN_DAILY_LIMIT: int = int(os.getenv("FUN_DAILY_LIMIT", "6"))
    FAN_TEST_FORCE_SEND: bool = os.getenv("FAN_TEST_FORCE_SEND", "0") == "1"
