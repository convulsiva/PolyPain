import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
    PARSER_BASE_URL: str = os.getenv("PARSER_BASE_URL", "")
    ENV: str = os.getenv("ENV", "dev")
    USER_FILE_PATH: str = os.getenv("USER_FILE_PATH", "storage/users.json")

