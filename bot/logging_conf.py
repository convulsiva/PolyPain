import logging
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

load_dotenv()

LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "logs/bot.log")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
DATE_FORMAT = os.getenv("DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

Path(LOG_FILE_NAME).parent.mkdir(parents=True, exist_ok=True)

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

    file_handler = logging.FileHandler(LOG_FILE_NAME, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])
