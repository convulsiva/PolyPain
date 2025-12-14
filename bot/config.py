from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

# bot/ → .env лежит здесь же
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass(slots=True)
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ENV: str = os.getenv("ENV", "dev")
    ADMIN_IDS: list[int] | None = None

    def __post_init__(self) -> None:
        raw_admins = os.getenv("ADMIN_IDS", "")
        self.ADMIN_IDS = [int(x) for x in raw_admins.split(",") if x.strip()]


config = Config()
