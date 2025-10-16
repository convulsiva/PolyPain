import logging
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

_env_log = os.getenv("LOG_FILE_NAME")
if _env_log:
    LOG_FILE_PATH = Path(_env_log)
    if not LOG_FILE_PATH.is_absolute():
        LOG_FILE_PATH = BASE_DIR / LOG_FILE_PATH
else:
    LOG_FILE_PATH = BASE_DIR / "logs" / "bot.log"

LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
DATE_FORMAT = os.getenv("DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

COLORS = {
    "DEBUG": "\033[90m",
    "INFO": "\033[92m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[41m",
}
RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLORS.get(record.levelname, RESET)
        message = super().format(record)
        return f"{log_color}{message}{RESET}"


def setup_logging():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler],
        force=True,
    )
