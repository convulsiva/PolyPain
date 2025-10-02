import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
    PARSER_BASE_URL: str = os.getenv("PARSER_BASE_URL", "")
    ENV: str = os.getenv("ENV", "dev")
    USER_FILE_PATH: str = os.getenv("USER_FILE_PATH", "storage/users.json")
    FUN_MIN_INTERVAL: int = int(os.getenv("FUN_MIN_INTERVAL", "1800"))   # 30 мин
    FUN_MAX_INTERVAL: int = int(os.getenv("FUN_MAX_INTERVAL", "5400"))   # 90 мин
    FAN_COOLDOWN_SECONDS: int = int(os.getenv("FAN_COOLDOWN_SECONDS", "1200"))  # 20 мин
    FUN_DAILY_LIMIT: int = int(os.getenv("FUN_DAILY_LIMIT", "6"))
    # форс-отправка в каждом цикле (0/1) в обычной работе держим 0.
    FAN_TEST_FORCE_SEND: bool = os.getenv("FAN_TEST_FORCE_SEND", "0") == "1"

