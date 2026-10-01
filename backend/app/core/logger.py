import logging
import sys
from logging.handlers import RotatingFileHandler

from app.core.config import LOG_DIR


def get_logger(name: str = "emergency") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:          # already set up, don't add handlers twice
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_DIR / "events.log", maxBytes=1_000_000, backupCount=3
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger