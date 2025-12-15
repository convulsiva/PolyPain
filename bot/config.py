from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Загружаем .env (если есть)
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


@dataclass(slots=True)
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ENV: str = os.getenv("ENV", "dev")

    LOG_FILE_NAME: str = os.getenv("LOG_FILE_NAME", "logs/bot.log")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    DATE_FORMAT: str = os.getenv("DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

    ADMIN_IDS: list[int] | None = None
    NOTIFY_BEFORE_MINUTES: int = int(os.getenv("NOTIFY_BEFORE_MINUTES", "60"))

    def __post_init__(self) -> None:
        raw_admins = os.getenv("ADMIN_IDS", "")
        self.ADMIN_IDS = [int(x.strip()) for x in raw_admins.split(",") if x.strip().isdigit()]


config = Config()
