import logging
from pathlib import Path
import sys

from bot.config import config


def setup_logging() -> None:
    log_file = Path(config.LOG_FILE_NAME)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=config.LOG_FORMAT,
        datefmt=config.DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )

    logging.getLogger("aiogram").setLevel(logging.WARNING)
